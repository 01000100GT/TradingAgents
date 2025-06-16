"""
该文件提供了各种数据流接口，用于获取金融市场数据、新闻和社交媒体数据，
以及进行技术分析和基本面分析。它整合了来自Finnhub、Google News、Reddit、
Yahoo Finance和SimFin的数据，并提供了数据处理和格式化功能，
以支持交易代理的决策过程。
"""

from typing import Annotated, Dict
from .reddit_utils import fetch_top_from_category
from .yfin_utils import *
from .stockstats_utils import *
from .googlenews_utils import *
from .finnhub_utils import get_data_in_range
from dateutil.relativedelta import relativedelta
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
import os
import pandas as pd
from tqdm import tqdm
import yfinance as yf
from openai import OpenAI
from .config import get_config, set_config, DATA_DIR


# DATA_DIR: 存储所有数据流生成的数据的目录。


def get_finnhub_news(
    ticker: Annotated[
        str,
        "Search query of a company's, e.g. 'AAPL, TSM, etc.",
    ],
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
):
    """
    检索公司在特定时间范围内的最新新闻

    参数:
        ticker (str): 感兴趣公司的股票代码，例如"AAPL"、"TSM"等。
        curr_date (str): 当前日期，格式为 yyyy-mm-dd。
        look_back_days (int): 回溯天数。

    返回:
        str: 包含指定时间范围内公司新闻的数据字符串。
    """

    start_date = datetime.strptime(curr_date, "%Y-%m-%d")
    before = start_date - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    result = get_data_in_range(ticker, before, curr_date, "news_data", DATA_DIR)

    if len(result) == 0:
        return ""

    combined_result = ""
    for day, data in result.items():
        if len(data) == 0:
            continue
        for entry in data:
            current_news = (
                "### " + entry["headline"] + f" ({day})" + "\n" + entry["summary"]
            )
            combined_result += current_news + "\n\n"

    return f"## {ticker} News, from {before} to {curr_date}:\n" + str(combined_result)


def get_finnhub_company_insider_sentiment(
    ticker: Annotated[str, "ticker symbol for the company"],
    curr_date: Annotated[
        str,
        "current date of you are trading at, yyyy-mm-dd",
    ],
    look_back_days: Annotated[int, "number of days to look back"],
):
    """
    检索公司（从公开 SEC 信息中获取）在过去指定天数的内部人情绪。

    参数:
        ticker (str): 公司股票代码。
        curr_date (str): 当前交易日期，格式为 yyyy-mm-dd。
        look_back_days (int): 回溯天数。

    返回:
        str: 从 curr_date 开始的过去指定天数的情绪报告。
    """

    date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    before = date_obj - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    data = get_data_in_range(ticker, before, curr_date, "insider_senti", DATA_DIR)

    if len(data) == 0:
        return ""

    result_str = ""
    seen_dicts = []
    for date, senti_list in data.items():
        for entry in senti_list:
            if entry not in seen_dicts:
                result_str += f"### {entry['year']}-{entry['month']}:\nChange: {entry['change']}\nMonthly Share Purchase Ratio: {entry['mspr']}\n\n"
                seen_dicts.append(entry)

    return (
        f"## {ticker} Insider Sentiment Data for {before} to {curr_date}:\n"
        + result_str
        + "The change field refers to the net buying/selling from all insiders' transactions. The mspr field refers to monthly share purchase ratio."
    )


def get_finnhub_company_insider_transactions(
    ticker: Annotated[str, "ticker symbol"],
    curr_date: Annotated[
        str,
        "current date you are trading at, yyyy-mm-dd",
    ],
    look_back_days: Annotated[int, "how many days to look back"],
):
    """
    检索公司（从公开 SEC 信息中获取）在过去指定天数的内部人交易信息。

    参数:
        ticker (str): 公司股票代码。
        curr_date (str): 当前交易日期，格式为 yyyy-mm-dd。
        look_back_days (int): 回溯天数。

    返回:
        str: 包含公司过去指定天数内部人交易/交易信息的报告。
    """

    date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    before = date_obj - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    data = get_data_in_range(ticker, before, curr_date, "insider_trans", DATA_DIR)

    if len(data) == 0:
        return ""

    result_str = ""

    seen_dicts = []
    for date, senti_list in data.items():
        for entry in senti_list:
            if entry not in seen_dicts:
                result_str += f"### Filing Date: {entry['filingDate']}, {entry['name']}:\nChange:{entry['change']}\nShares: {entry['share']}\nTransaction Price: {entry['transactionPrice']}\nTransaction Code: {entry['transactionCode']}\n\n"
                seen_dicts.append(entry)

    return (
        f"## {ticker} insider transactions from {before} to {curr_date}:\n"
        + result_str
        + "The change field reflects the variation in share count—here a negative number indicates a reduction in holdings—while share specifies the total number of shares involved. The transactionPrice denotes the per-share price at which the trade was executed, and transactionDate marks when the transaction occurred. The name field identifies the insider making the trade, and transactionCode (e.g., S for sale) clarifies the nature of the transaction. FilingDate records when the transaction was officially reported, and the unique id links to the specific SEC filing, as indicated by the source. Additionally, the symbol ties the transaction to a particular company, isDerivative flags whether the trade involves derivative securities, and currency notes the currency context of the transaction."
    )


def get_simfin_balance_sheet(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[
        str,
        "reporting frequency of the company's financial history: annual / quarterly",
    ],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
):
    """
    获取公司在给定日期的SimFin资产负债表。

    参数:
        ticker (str): 股票代码。
        freq (str): 报告频率，可以是 'annual'（年度）或 'quarterly'（季度）。
        curr_date (str): 当前交易日期，格式为 yyyy-mm-dd。

    返回:
        str: 公司最新的资产负债表数据。如果在此日期之前没有可用的报告，则返回空字符串。
    """
    data_path = os.path.join(
        DATA_DIR,
        "fundamental_data",
        "simfin_data_all",
        "balance_sheet",
        "companies",
        "us",
        f"us-balance-{freq}.csv",
    )
    df = pd.read_csv(data_path, sep=";")

    # 将日期字符串转换为 datetime 对象并移除时间部分
    df["Report Date"] = pd.to_datetime(df["Report Date"], utc=True).normalize()
    df["Publish Date"] = pd.to_datetime(df["Publish Date"], utc=True).normalize()

    # 将当前日期转换为 datetime 并标准化
    curr_date_dt = pd.to_datetime(curr_date, utc=True).normalize()

    # 过滤 DataFrame，获取给定股票代码且发布日期在当前日期或之前的报告
    filtered_df = df[(df["Ticker"] == ticker) & (df["Publish Date"] <= curr_date_dt)]

    # 检查是否有可用的报告；如果没有，则返回通知
    if filtered_df.empty:
        print("在给定当前日期之前没有可用的资产负债表。")
        return ""

    # 通过选择最新发布日期的行来获取最新的资产负债表
    latest_balance_sheet = filtered_df.loc[filtered_df["Publish Date"].idxmax()]

    # 丢弃 SimFinID 列
    latest_balance_sheet = latest_balance_sheet.drop("SimFinId")

    return (
        f"## {freq} balance sheet for {ticker} released on {str(latest_balance_sheet['Publish Date'])[0:10]}: \n"
        + str(latest_balance_sheet)
        + "\n\nThis includes metadata like reporting dates and currency, share details, and a breakdown of assets, liabilities, and equity. Assets are grouped as current (liquid items like cash and receivables) and noncurrent (long-term investments and property). Liabilities are split between short-term obligations and long-term debts, while equity reflects shareholder funds such as paid-in capital and retained earnings. Together, these components ensure that total assets equal the sum of liabilities and equity."
    )


def get_simfin_cashflow(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[
        str,
        "reporting frequency of the company's financial history: annual / quarterly",
    ],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
):
    """
    获取公司在给定日期的SimFin现金流量表。

    参数:
        ticker (str): 股票代码。
        freq (str): 报告频率，可以是 'annual'（年度）或 'quarterly'（季度）。
        curr_date (str): 当前交易日期，格式为 yyyy-mm-dd。

    返回:
        str: 公司最新的现金流量表数据。如果在此日期之前没有可用的报告，则返回空字符串。
    """
    data_path = os.path.join(
        DATA_DIR,
        "fundamental_data",
        "simfin_data_all",
        "cash_flow",
        "companies",
        "us",
        f"us-cashflow-{freq}.csv",
    )
    df = pd.read_csv(data_path, sep=";")

    # 将日期字符串转换为 datetime 对象并移除时间部分
    df["Report Date"] = pd.to_datetime(df["Report Date"], utc=True).normalize()
    df["Publish Date"] = pd.to_datetime(df["Publish Date"], utc=True).normalize()

    # 将当前日期转换为 datetime 并标准化
    curr_date_dt = pd.to_datetime(curr_date, utc=True).normalize()

    # 过滤 DataFrame，获取给定股票代码且发布日期在当前日期或之前的报告
    filtered_df = df[(df["Ticker"] == ticker) & (df["Publish Date"] <= curr_date_dt)]

    # 检查是否有可用的报告；如果没有，则返回通知
    if filtered_df.empty:
        print("在给定当前日期之前没有可用的现金流量表。")
        return ""

    # 通过选择最新发布日期的行来获取最新的现金流量表
    latest_cash_flow = filtered_df.loc[filtered_df["Publish Date"].idxmax()]

    # 丢弃 SimFinID 列
    latest_cash_flow = latest_cash_flow.drop("SimFinId")

    return (
        f"## {freq} cash flow statement for {ticker} released on {str(latest_cash_flow['Publish Date'])[0:10]}: \n"
        + str(latest_cash_flow)
        + "\n\nThis includes metadata like reporting dates and currency, share details, and a breakdown of cash movements. Operating activities show cash generated from core business operations, including net income adjustments for non-cash items and working capital changes. Investing activities cover asset acquisitions/disposals and investments. Financing activities include debt transactions, equity issuances/repurchases, and dividend payments. The net change in cash represents the overall increase or decrease in the company's cash position during the reporting period."
    )


def get_simfin_income_statements(
    ticker: Annotated[str, "ticker symbol"],
    freq: Annotated[
        str,
        "reporting frequency of the company's financial history: annual / quarterly",
    ],
    curr_date: Annotated[str, "current date you are trading at, yyyy-mm-dd"],
):
    """
    获取公司在给定日期的SimFin利润表。

    参数:
        ticker (str): 股票代码。
        freq (str): 报告频率，可以是 'annual'（年度）或 'quarterly'（季度）。
        curr_date (str): 当前交易日期，格式为 yyyy-mm-dd。

    返回:
        str: 公司最新的利润表数据。如果在此日期之前没有可用的报告，则返回空字符串。
    """
    data_path = os.path.join(
        DATA_DIR,
        "fundamental_data",
        "simfin_data_all",
        "income_statements",
        "companies",
        "us",
        f"us-income-{freq}.csv",
    )
    df = pd.read_csv(data_path, sep=";")

    # 将日期字符串转换为 datetime 对象并移除时间部分
    df["Report Date"] = pd.to_datetime(df["Report Date"], utc=True).normalize()
    df["Publish Date"] = pd.to_datetime(df["Publish Date"], utc=True).normalize()

    # 将当前日期转换为 datetime 并标准化
    curr_date_dt = pd.to_datetime(curr_date, utc=True).normalize()

    # 过滤 DataFrame，获取给定股票代码且发布日期在当前日期或之前的报告
    filtered_df = df[(df["Ticker"] == ticker) & (df["Publish Date"] <= curr_date_dt)]

    # 检查是否有可用的报告；如果没有，则返回通知
    if filtered_df.empty:
        print("在给定当前日期之前没有可用的利润表。")
        return ""

    # 通过选择最新发布日期的行来获取最新的利润表
    latest_income = filtered_df.loc[filtered_df["Publish Date"].idxmax()]

    # 丢弃 SimFinID 列
    latest_income = latest_income.drop("SimFinId")

    return (
        f"## {freq} income statement for {ticker} released on {str(latest_income['Publish Date'])[0:10]}: \n"
        + str(latest_income)
        + "\n\nThis includes metadata like reporting dates and currency, share details, and a comprehensive breakdown of the company's financial performance. Starting with Revenue, it shows Cost of Revenue and resulting Gross Profit. Operating Expenses are detailed, including SG&A, R&D, and Depreciation. The statement then shows Operating Income, followed by non-operating items and Interest Expense, leading to Pretax Income. After accounting for Income Tax and any Extraordinary items, it concludes with Net Income, representing the company's bottom-line profit or loss for the period."
    )


def get_google_news(
    query: Annotated[str, "Query to search with"],
    curr_date: Annotated[str, "Curr date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:
    """
    使用 Google News 检索新闻。

    参数:
        query (str): 搜索查询。
        curr_date (str): 当前日期，格式为 yyyy-mm-dd。
        look_back_days (int): 回溯天数。

    返回:
        str: 格式化的新闻字符串。
    """
    query = query.replace(" ", "+")

    start_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    before = start_date_dt - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    news_results = getNewsData(query, before, curr_date)

    news_str = ""

    for news in news_results:
        news_str += (
            f"### {news['title']} (source: {news['source']}) \n\n{news['snippet']}\n\n"
        )

    if len(news_results) == 0:
        return ""

    return f"## {query} Google News, from {before} to {curr_date}:\n\n{news_str}"


def get_reddit_global_news(
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
    max_limit_per_day: Annotated[int, "Maximum number of news per day"],
) -> str:
    """
    检索 Reddit 上的最新热门全球新闻。

    参数:
        start_date (str): 开始日期，格式为 yyyy-mm-dd。
        look_back_days (int): 回溯天数。
        max_limit_per_day (int): 每天最大新闻数量。

    返回:
        str: 包含 Reddit 上最新新闻文章及其元信息的格式化字符串。
    """

    start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
    before = start_date_dt - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    posts = []
    # 从 start_date 迭代到 end_date
    curr_date_dt = datetime.strptime(before, "%Y-%m-%d")

    total_iterations = (start_date_dt - curr_date_dt).days + 1
    pbar = tqdm(desc=f"正在获取 {start_date} 的全球新闻", total=total_iterations)

    while curr_date_dt <= start_date_dt:
        curr_date_str = curr_date_dt.strftime("%Y-%m-%d")
        fetch_result = fetch_top_from_category(
            "global_news",
            curr_date_str,
            max_limit_per_day,
            data_path=os.path.join(str(DATA_DIR), "reddit_data"),
        )
        posts.extend(fetch_result)
        curr_date_dt += relativedelta(days=1)
        pbar.update(1)

    pbar.close()

    if len(posts) == 0:
        return ""

    news_str = ""
    for post in posts:
        if post["content"] == "":
            news_str += f"### {post['title']}\n\n"
        else:
            news_str += f"### {post['title']}\n\n{post['content']}\n\n"

    return f"## Global News Reddit, from {before} to {curr_date}:\n{news_str}"


def get_reddit_company_news(
    ticker: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
    max_limit_per_day: Annotated[int, "Maximum number of news per day"],
) -> str:
    """
    检索 Reddit 上公司的最新热门新闻。

    参数:
        ticker (str): 公司股票代码。
        start_date (str): 开始日期，格式为 yyyy-mm-dd。
        look_back_days (int): 回溯天数。
        max_limit_per_day (int): 每天最大新闻数量。

    返回:
        str: 包含 Reddit 上最新新闻文章及其元信息的格式化字符串。
    """

    start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
    before = start_date_dt - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    posts = []
    # 从 start_date 迭代到 end_date
    curr_date_dt = datetime.strptime(before, "%Y-%m-%d")

    total_iterations = (start_date_dt - curr_date_dt).days + 1
    pbar = tqdm(
        desc=f"正在获取 {ticker} 在 {start_date} 的公司新闻",
        total=total_iterations,
    )

    while curr_date_dt <= start_date_dt:
        curr_date_str = curr_date_dt.strftime("%Y-%m-%d")
        fetch_result = fetch_top_from_category(
            "company_news",
            curr_date_str,
            max_limit_per_day,
            ticker,
            data_path=os.path.join(str(DATA_DIR), "reddit_data"),
        )
        posts.extend(fetch_result)
        curr_date_dt += relativedelta(days=1)

        pbar.update(1)

    pbar.close()

    if len(posts) == 0:
        return ""

    news_str = ""
    for post in posts:
        if post["content"] == "":
            news_str += f"### {post['title']}\n\n"
        else:
            news_str += f"### {post['title']}\n\n{post['content']}\n\n"

    return f"##{ticker} News Reddit, from {before} to {curr_date}:\n\n{news_str}"


def get_stock_stats_indicators_window(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[
        str, "The current trading date you are trading on, YYYY-mm-dd"
    ],
    look_back_days: Annotated[int, "how many days to look back"],
    online: Annotated[bool, "to fetch data online or offline"],
) -> str:
    """
    获取指定技术指标在特定时间窗口内的值。

    参数:
        symbol (str): 公司股票代码。
        indicator (str): 要获取分析和报告的技术指标。
        curr_date (str): 当前交易日期，格式为 YYYY-mm-dd。
        look_back_days (int): 回溯天数。
        online (bool): 是否在线获取数据。

    返回:
        str: 包含指定技术指标在时间窗口内值的报告。
    """

    best_ind_params = {
        # 移动平均线
        "close_50_sma": (
            "50 日简单移动平均线（50 SMA）：中期趋势指标。 "
            "用途：识别趋势方向并作为动态支撑/阻力。 "
            "提示：它滞后于价格；结合更快的指标以获取及时信号。"
        ),
        "close_200_sma": (
            "200 日简单移动平均线（200 SMA）：长期趋势基准。 "
            "用途：确认整体市场趋势并识别金叉/死叉形态。 "
            "提示：它反应缓慢；最适合用于战略趋势确认而非频繁的交易入场。"
        ),
        "close_10_ema": (
            "10 日指数移动平均线（10 EMA）：响应式短期平均线。 "
            "用途：捕捉动量的快速变化和潜在的入场点。 "
            "提示：在震荡市场中容易出现噪音；与较长的平均线一起使用以过滤假信号。"
        ),
        # MACD 相关
        "macd": (
            "MACD：通过 EMA 差异计算动量。 "
            "用途：寻找交叉和背离作为趋势变化的信号。 "
            "提示：在低波动或横盘市场中与其他指标结合确认。"
        ),
        "macds": (
            "MACD 信号线：MACD 线的 EMA 平滑。 "
            "用途：使用与 MACD 线的交叉来触发交易。 "
            "提示：应作为更广泛策略的一部分，以避免假阳性。"
        ),
        "macdh": (
            "MACD 柱状图：显示 MACD 线与其信号线之间的差距。 "
            "用途：可视化动量强度并及早发现背离。 "
            "提示：可能波动较大；在快速变化的市场中补充额外的过滤器。"
        ),
        # 动量指标
        "rsi": (
            "RSI：衡量动量以标记超买/超卖情况。 "
            "用途：应用 70/30 阈值并观察背离以发出反转信号。 "
            "提示：在强劲趋势中，RSI 可能保持极端；始终与趋势分析交叉检查。"
        ),
        # 波动率指标
        "boll": (
            "布林带中轨：作为布林带基础的 20 日简单移动平均线。 "
            "用途：作为价格波动的动态基准。 "
            "提示：与上轨和下轨结合使用，有效发现突破或反转。"
        ),
        "boll_ub": (
            "布林带上轨：通常在中线以上 2 个标准差。 "
            "用途：表示潜在的超买情况和突破区域。 "
            "提示：使用其他工具确认信号；价格在强劲趋势中可能沿着布林带运行。"
        ),
        "boll_lb": (
            "布林带下轨：通常在中线以下 2 个标准差。 "
            "用途：表示潜在的超卖情况。 "
            "提示：使用额外分析以避免错误的逆转信号。"
        ),
        "atr": (
            "ATR：平均真实波动范围，衡量波动性。 "
            "用途：根据当前市场波动性设置止损水平和调整头寸规模。 "
            "提示：它是一种反应性指标，因此将其作为更广泛风险管理策略的一部分。"
        ),
        # 成交量指标
        "vwma": (
            "VWMA：成交量加权移动平均线。 "
            "用途：通过整合价格行为和成交量数据来确认趋势。 "
            "提示：注意成交量飙升导致的倾斜结果；结合其他成交量分析一起使用。"
        ),
        "mfi": (
            "MFI：资金流量指标是一种动量指标，同时使用价格和成交量来衡量买卖压力。 "
            "用途：识别超买（>80）或超卖（<20）情况，并确认趋势或反转的强度。 "
            "提示：与 RSI 或 MACD 一起使用以确认信号；价格和 MFI 之间的背离可能预示着潜在的反转。"
        ),
    }

    if indicator not in best_ind_params:
        raise ValueError(
            f"指标 {indicator} 不受支持。请从以下选项中选择：{list(best_ind_params.keys())}"
        )

    end_date = curr_date
    curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    before_dt = curr_date_dt - relativedelta(days=look_back_days)

    if not online:
        # 从 YFin 数据读取
        data = pd.read_csv(
            os.path.join(
                str(DATA_DIR),
                f"market_data/price_data/{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
            )
        )
        data["Date"] = pd.to_datetime(data["Date"], utc=True)
        dates_in_df = data["Date"].astype(str).str[:10]

        ind_string = ""
        while curr_date_dt >= before_dt:
            # 只处理交易日期
            if curr_date_dt.strftime("%Y-%m-%d") in dates_in_df.values:
                indicator_value = get_stockstats_indicator(
                    symbol, indicator, curr_date_dt.strftime("%Y-%m-%d"), online
                )

                ind_string += (
                    f"{curr_date_dt.strftime('%Y-%m-%d')}: {indicator_value}\n"
                )

            curr_date_dt = curr_date_dt - relativedelta(days=1)
    else:
        # 在线获取
        ind_string = ""
        while curr_date_dt >= before_dt:
            indicator_value = get_stockstats_indicator(
                symbol, indicator, curr_date_dt.strftime("%Y-%m-%d"), online
            )

            ind_string += f"{curr_date_dt.strftime('%Y-%m-%d')}: {indicator_value}\n"

            curr_date_dt = curr_date_dt - relativedelta(days=1)

    result_str = (
        f"## {indicator} 值从 {before_dt.strftime('%Y-%m-%d')} 到 {end_date}:\n\n"
        + ind_string
        + "\n\n"
        + best_ind_params.get(indicator, "无可用描述。")
    )

    return result_str


def get_stockstats_indicator(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[
        str, "The current trading date you are trading on, YYYY-mm-dd"
    ],
    online: Annotated[bool, "to fetch data online or offline"],
) -> str:
    """
    获取指定技术指标在给定日期的值。

    参数:
        symbol (str): 公司股票代码。
        indicator (str): 要获取分析和报告的技术指标。
        curr_date (str): 当前交易日期，格式为 YYYY-mm-dd。
        online (bool): 是否在线获取数据。

    返回:
        str: 指定技术指标的值。如果获取数据失败，则返回空字符串。
    """

    curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    curr_date_str = curr_date_dt.strftime("%Y-%m-%d")

    try:
        indicator_value = StockstatsUtils.get_stock_stats(
            symbol,
            indicator,
            curr_date_str,
            os.path.join(str(DATA_DIR), "market_data", "price_data"),
            online=online,
        )
    except Exception as e:
        print(f"获取指标 {indicator} 在 {curr_date} 的 stockstats 指标数据时出错: {e}")
        return ""

    return str(indicator_value)


def get_YFin_data_window(
    symbol: Annotated[str, "ticker symbol of the company"],
    curr_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:
    """
    获取指定股票在特定时间窗口内的 Yahoo Finance 市场数据（离线）。

    参数:
        symbol (str): 公司股票代码。
        curr_date (str): 当前日期，格式为 yyyy-mm-dd。
        look_back_days (int): 回溯天数。

    返回:
        str: 包含指定时间范围内股票原始市场数据的字符串。
    """
    # 计算过去天数
    date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    before = date_obj - relativedelta(days=look_back_days)
    start_date = before.strftime("%Y-%m-%d")

    # 读取数据
    data = pd.read_csv(
        os.path.join(
            str(DATA_DIR),
            f"market_data/price_data/{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
        )
    )

    # Extract just the date part for comparison
    data["DateOnly"] = data["Date"].str[:10]

    # Filter data between the start and end dates (inclusive)
    filtered_data = data[
        (data["DateOnly"] >= start_date) & (data["DateOnly"] <= curr_date)
    ]

    # Drop the temporary column we created
    filtered_data = filtered_data.drop("DateOnly", axis=1)

    # Set pandas display options to show the full DataFrame
    with pd.option_context(
        "display.max_rows", None, "display.max_columns", None, "display.width", None
    ):
        df_string = filtered_data.to_string()

    return (
        f"## Raw Market Data for {symbol} from {start_date} to {curr_date}:\n\n"
        + df_string
    )


def get_YFin_data_online(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "Start date in yyyy-mm-dd format"],
):
    """
    在线获取指定股票在特定日期范围内的 Yahoo Finance 市场数据。

    参数:
        symbol (str): 公司股票代码。
        start_date (str): 开始日期，格式为 yyyy-mm-dd。
        end_date (str): 结束日期，格式为 yyyy-mm-dd。

    返回:
        str: 包含指定日期范围内股票市场数据的 CSV 格式字符串。
    """

    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")

    # Create ticker object
    ticker = yf.Ticker(symbol.upper())

    # Fetch historical data for the specified date range
    data = ticker.history(start=start_date, end=end_date)

    # Check if data is empty
    if data.empty:
        return (
            f"No data found for symbol '{symbol}' between {start_date} and {end_date}"
        )

    # Remove timezone info from index for cleaner output
    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)

    # Round numerical values to 2 decimal places for cleaner display
    numeric_columns = ["Open", "High", "Low", "Close", "Adj Close"]
    for col in numeric_columns:
        if col in data.columns:
            data[col] = data[col].round(2)

    # Convert DataFrame to CSV string
    csv_string = data.to_csv()

    # Add header information
    header = f"# Stock data for {symbol.upper()} from {start_date} to {end_date}\n"
    header += f"# Total records: {len(data)}\n"
    header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    return header + csv_string


def get_YFin_data(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "Start date in yyyy-mm-dd format"],
) -> str:
    """
    获取指定股票在特定日期范围内的 Yahoo Finance 市场数据（离线）。

    参数:
        symbol (str): 公司股票代码。
        start_date (str): 开始日期，格式为 yyyy-mm-dd。
        end_date (str): 结束日期，格式为 yyyy-mm-dd。

    返回:
        pd.DataFrame: 包含指定日期范围内股票市场数据的 DataFrame。
    """
    # read in data
    data = pd.read_csv(
        os.path.join(
            str(DATA_DIR),
            f"market_data/price_data/{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
        )
    )

    if end_date > "2025-03-25":
        raise Exception(
            f"Get_YFin_Data: {end_date} 超出数据范围 2015-01-01 到 2025-03-25"
        )

    # Extract just the date part for comparison
    data["DateOnly"] = data["Date"].str[:10]

    # Filter data between the start and end dates (inclusive)
    filtered_data = data[
        (data["DateOnly"] >= start_date) & (data["DateOnly"] <= end_date)
    ]

    # Drop the temporary column we created
    filtered_data = filtered_data.drop("DateOnly", axis=1)

    # remove the index from the dataframe
    filtered_data = filtered_data.reset_index(drop=True)

    with pd.option_context(
        "display.max_rows", None, "display.max_columns", None, "display.width", None
    ):
        df_string = filtered_data.to_string()

    return df_string


def get_stock_news_openai(ticker, curr_date):
    """
    使用 OpenAI 搜索指定股票在特定日期范围内的社交媒体新闻。

    参数:
        ticker: 股票代码。
        curr_date: 当前日期。

    返回:
        str: 社交媒体新闻报告。
    """
    config = get_config()
    model_config = config.get("model_config", {})
    client = OpenAI(
        base_url=model_config.get("base_url"),
        api_key=model_config.get("api_key")
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Can you search Social Media for {ticker} from 7 days before {curr_date} to {curr_date}? Make sure you only get the data posted during that period.",
                    }
                ],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[
            {
                "type": "web_search_preview",
                "user_location": {"type": "approximate"},
                "search_context_size": "low",
            }
        ],
        temperature=1,
        max_output_tokens=4096,
        top_p=1,
        store=True,
    )

    return response.output[1].content[0].text


def get_global_news_openai(curr_date):
    """
    使用 OpenAI 搜索指定日期范围内的全球或宏观经济新闻。

    参数:
        curr_date: 当前日期。

    返回:
        str: 全球或宏观经济新闻报告。
    """
    config = get_config()
    model_config = config.get("model_config", {})
    client = OpenAI(
        base_url=model_config.get("base_url"),
        api_key=model_config.get("api_key")
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Can you search global or macroeconomics news from 7 days before {curr_date} to {curr_date} that would be informative for trading purposes? Make sure you only get the data posted during that period.",
                    }
                ],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[
            {
                "type": "web_search_preview",
                "user_location": {"type": "approximate"},
                "search_context_size": "low",
            }
        ],
        temperature=1,
        max_output_tokens=4096,
        top_p=1,
        store=True,
    )

    return response.output[1].content[0].text


def get_fundamentals_openai(ticker, curr_date):
    """
    使用 OpenAI 搜索指定股票在特定日期范围内的基本面讨论。

    参数:
        ticker: 股票代码。
        curr_date: 当前日期。

    返回:
        str: 基本面讨论报告。
    """
    config = get_config()
    model_config = config.get("model_config", {})
    client = OpenAI(
        base_url=model_config.get("base_url"),
        api_key=model_config.get("api_key")
    )

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Can you search Fundamental for discussions on {ticker} during of the month before {curr_date} to the month of {curr_date}. Make sure you only get the data posted during that period. List as a table, with PE/PS/Cash flow/ etc",
                    }
                ],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[
            {
                "type": "web_search_preview",
                "user_location": {"type": "approximate"},
                "search_context_size": "low",
            }
        ],
        temperature=1,
        max_output_tokens=4096,
        top_p=1,
        store=True,
    )

    return response.output[1].content[0].text
