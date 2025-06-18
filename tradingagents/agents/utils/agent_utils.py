# 本文件包含了一系列工具函数，用于交易代理获取各种市场数据和金融信息。

from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage
from typing import List
from typing import Annotated
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import RemoveMessage
from langchain_core.tools import tool
from datetime import date, timedelta, datetime
import functools
import pandas as pd
import os
from dateutil.relativedelta import relativedelta
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import tradingagents.dataflows.interface as interface
from tradingagents.default_config import DEFAULT_CONFIG


# 创建ChatOpenAI模型实例
def create_chat_openai(config, model_name=None, temperature=0.7):
    """
    根据配置创建ChatOpenAI模型实例
    Args:
        config: 配置字典
        model_name: 模型名称，如果为None则使用配置中的默认模型
        temperature: 温度参数
    Returns:
        ChatOpenAI实例
    """
    model_config = config.get("model_config", {})
    
    # 构建ChatOpenAI参数
    chat_params = {
        "model": model_name or model_config.get("model", "gpt-4o-mini"),
        "temperature": temperature,
    }
    
    # 添加base_url和api_key（如果存在）
    if model_config.get("base_url"):
        chat_params["base_url"] = model_config["base_url"]
    if model_config.get("api_key"):
        chat_params["api_key"] = model_config["api_key"]
    
    return ChatOpenAI(**chat_params)

# 创建OpenAI嵌入模型实例
def create_openai_embeddings(config):
    """
    根据配置创建OpenAI嵌入模型实例
    Args:
        config: 配置字典
    Returns:
        OpenAIEmbeddings实例
    """
    model_config = config.get("model_config", {})
    
    # 构建OpenAIEmbeddings参数
    embedding_params = {
        "model": config.get("embedding_model", "text-embedding-3-small"),
    }
    
    # 添加base_url和api_key（如果存在）
    embedding_base_url = config.get("embedding_base_url") or model_config.get("base_url")
    embedding_api_key = config.get("embedding_api_key") or model_config.get("api_key")
    
    if embedding_base_url:
        embedding_params["base_url"] = embedding_base_url
    if embedding_api_key:
        embedding_params["api_key"] = embedding_api_key
    
    return OpenAIEmbeddings(**embedding_params)

# 创建消息删除函数
def create_msg_delete():
    # 删除消息，防止消息历史溢出
    def delete_messages(state):
        """为防止消息历史溢出，在流水线的某个阶段完成后定期清除消息历史"""
        messages = state["messages"]
        return {"messages": [RemoveMessage(id=m.id) for m in messages]}

    return delete_messages


# 工具箱类，提供各种数据获取工具
class Toolkit:
    _config = DEFAULT_CONFIG.copy()

    @classmethod
    # 更新类级别的配置
    def update_config(cls, config):
        """更新类级别的配置。"""
        cls._config.update(config)

    @property
    # 访问配置
    def config(self):
        """访问配置。"""
        return self._config

    # 初始化方法
    def __init__(self, config=None):
        if config:
            self.update_config(config)

    @staticmethod
    @tool
    # 获取 Reddit 新闻
    def get_reddit_news(
        curr_date: Annotated[str, "您想要获取新闻的日期，格式为yyyy-mm-dd"],
    ) -> str:
        """
        在指定时间范围内从Reddit检索全球新闻。
        Args:
            curr_date (str): 您想要获取新闻的日期，格式为yyyy-mm-dd
        Returns:
            str: 包含指定时间范围内来自Reddit的最新全球新闻的格式化数据框。
        """

        global_news_result = interface.get_reddit_global_news(curr_date, 7, 5)

        return global_news_result

    @staticmethod
    @tool
    # 获取 Finnhub 新闻
    def get_finnhub_news(
        ticker: Annotated[
            str,
            "公司的搜索查询，例如 'AAPL, TSM, 等'",
        ],
        start_date: Annotated[str, "开始日期，格式为yyyy-mm-dd"],
        end_date: Annotated[str, "结束日期，格式为yyyy-mm-dd"],
    ):
        """
        在日期范围内从Finnhub检索关于给定股票的最新新闻
        Args:
            ticker (str): 公司的股票代码。例如 AAPL, TSM
            start_date (str): 开始日期，格式为yyyy-mm-dd
            end_date (str): 结束日期，格式为yyyy-mm-dd
        Returns:
            str: 包含从start_date到end_date日期范围内公司新闻的格式化数据框
        """

        end_date_str = end_date

        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        look_back_days = (end_date - start_date).days

        finnhub_news_result = interface.get_finnhub_news(
            ticker, end_date_str, look_back_days
        )

        return finnhub_news_result

    @staticmethod
    @tool
    # 获取 Reddit 股票信息
    def get_reddit_stock_info(
        ticker: Annotated[
            str,
            "公司的股票代码。例如 AAPL, TSM",
        ],
        curr_date: Annotated[str, "您想要获取新闻的当前日期"],
    ) -> str:
        """
        根据当前日期从Reddit检索关于给定股票的最新新闻。
        Args:
            ticker (str): 公司的股票代码。例如 AAPL, TSM
            curr_date (str): 获取新闻的当前日期，格式为yyyy-mm-dd
        Returns:
            str: 包含给定日期公司最新新闻的格式化数据框
        """

        stock_news_results = interface.get_reddit_company_news(ticker, curr_date, 7, 5)

        return stock_news_results

    @staticmethod
    @tool
    # 获取 Yahoo Finance 数据
    def get_YFin_data(
        symbol: Annotated[str, "公司的股票代码"],
        start_date: Annotated[str, "开始日期，格式为yyyy-mm-dd"],
        end_date: Annotated[str, "结束日期，格式为yyyy-mm-dd"],
    ) -> str:
        """
        从Yahoo Finance检索给定股票代码的股价数据。
        Args:
            symbol (str): 公司的股票代码，例如 AAPL, TSM
            start_date (str): 开始日期，格式为yyyy-mm-dd
            end_date (str): 结束日期，格式为yyyy-mm-dd
        Returns:
            str: 包含指定日期范围内指定股票代码股价数据的格式化数据框。
        """

        result_data = interface.get_YFin_data(symbol, start_date, end_date)

        return result_data

    @staticmethod
    @tool
    # 在线获取 Yahoo Finance 数据
    def get_YFin_data_online(
        symbol: Annotated[str, "公司的股票代码"],
        start_date: Annotated[str, "开始日期，格式为yyyy-mm-dd"],
        end_date: Annotated[str, "结束日期，格式为yyyy-mm-dd"],
    ) -> str:
        """
        从Yahoo Finance检索给定股票代码的股价数据。
        Args:
            symbol (str): 公司的股票代码，例如 AAPL, TSM
            start_date (str): 开始日期，格式为yyyy-mm-dd
            end_date (str): 结束日期，格式为yyyy-mm-dd
        Returns:
            str: 包含指定日期范围内指定股票代码股价数据的格式化数据框。
        """

        result_data = interface.get_YFin_data_online(symbol, stget_stockstats_indicators_reportart_date, end_date)

        return result_data

    @staticmethod
    @tool
    # 获取股票统计指标报告
    def get_stockstats_indicators_report(
        symbol: Annotated[str, "公司的股票代码"],
        indicator: Annotated[
            str, "要获取分析和报告的技术指标"
        ],
        curr_date: Annotated[
            str, "您正在交易的当前交易日期，格式为YYYY-mm-dd"
        ],
        look_back_days: Annotated[int, "回看多少天"] = 30,
    ) -> str:
        """
        检索给定股票代码和指标的股票统计指标。
        Args:
            symbol (str): 公司的股票代码，例如 AAPL, TSM
            indicator (str): 要获取分析和报告的技术指标
            curr_date (str): 您正在交易的当前交易日期，格式为YYYY-mm-dd
            look_back_days (int): 回看多少天，默认为30天
        Returns:
            str: 包含指定股票代码和指标的股票统计指标的格式化数据框。
        """

        result_stockstats = interface.get_stock_stats_indicators_window(
            symbol, indicator, curr_date, look_back_days, False
        )

        return result_stockstats

    @staticmethod
    @tool
    # 在线获取股票统计指标报告
    def get_stockstats_indicators_report_online(
        symbol: Annotated[str, "公司的股票代码"],
        indicator: Annotated[
            str, "要获取分析和报告的技术指标"
        ],
        curr_date: Annotated[
            str, "您正在交易的当前交易日期，格式为YYYY-mm-dd"
        ],
        look_back_days: Annotated[int, "回看多少天"] = 30,
    ) -> str:
        """
        检索给定股票代码和指标的股票统计指标。
        Args:
            symbol (str): 公司的股票代码，例如 AAPL, TSM
            indicator (str): 要获取分析和报告的技术指标
            curr_date (str): 您正在交易的当前交易日期，格式为YYYY-mm-dd
            look_back_days (int): 回看多少天，默认为30天
        Returns:
            str: 包含指定股票代码和指标的股票统计指标的格式化数据框。
        """

        result_stockstats = interface.get_stock_stats_indicators_window(
            symbol, indicator, curr_date, look_back_days, True
        )

        return result_stockstats

    @staticmethod
    @tool
    # 获取 Finnhub 公司内部人士情绪
    def get_finnhub_company_insider_sentiment(
        ticker: Annotated[str, "公司的股票代码"],
        curr_date: Annotated[
            str,
            "您正在交易的当前日期，格式为yyyy-mm-dd",
        ],
    ):
        """
        检索公司的内部人士情绪信息（从公开的SEC信息中获取），过去30天
        Args:
            ticker (str): 公司的股票代码
            curr_date (str): 您正在交易的当前日期，格式为yyyy-mm-dd
        Returns:
            str: 从curr_date开始过去30天的情绪报告
        """

        data_sentiment = interface.get_finnhub_company_insider_sentiment(
            ticker, curr_date, 30
        )

        return data_sentiment

    @staticmethod
    @tool
    # 获取 Finnhub 公司内部人士交易
    def get_finnhub_company_insider_transactions(
        ticker: Annotated[str, "公司的股票代码"],
        curr_date: Annotated[
            str,
            "您正在交易的当前日期，格式为yyyy-mm-dd",
        ],
    ):
        """
        检索公司的内部人士交易信息（从公开的SEC信息中获取），过去30天
        Args:
            ticker (str): 公司的股票代码
            curr_date (str): 您正在交易的当前日期，格式为yyyy-mm-dd
        Returns:
            str: 过去30天公司内部人士交易/买卖信息的报告
        """

        data_trans = interface.get_finnhub_company_insider_transactions(
            ticker, curr_date, 30
        )

        return data_trans

    @staticmethod
    @tool
    # 获取 Simfin 资产负债表
    def get_simfin_balance_sheet(
        ticker: Annotated[str, "公司的股票代码"],
        freq: Annotated[
            str,
            "公司财务历史的报告频率：年度/季度",
        ],
        curr_date: Annotated[str, "您正在交易的当前日期，格式为yyyy-mm-dd"],
    ):
        """
        检索公司最新的资产负债表
        Args:
            ticker (str): 公司的股票代码
            freq (str): 公司财务历史的报告频率：年度/季度
            curr_date (str): 您正在交易的当前日期，格式为yyyy-mm-dd
        Returns:
            str: 公司最新资产负债表的报告
        """

        data_balance_sheet = interface.get_simfin_balance_sheet(ticker, freq, curr_date)

        return data_balance_sheet

    @staticmethod
    @tool
    # 获取 Simfin 现金流量表
    def get_simfin_cashflow(
        ticker: Annotated[str, "公司的股票代码"],
        freq: Annotated[
            str,
            "公司财务历史的报告频率：年度/季度",
        ],
        curr_date: Annotated[str, "您正在交易的当前日期，格式为yyyy-mm-dd"],
    ):
        """
        检索公司最新的现金流量表
        Args:
            ticker (str): 公司的股票代码
            freq (str): 公司财务历史的报告频率：年度/季度
            curr_date (str): 您正在交易的当前日期，格式为yyyy-mm-dd
        Returns:
                str: 公司最新现金流量表的报告
        """

        data_cashflow = interface.get_simfin_cashflow(ticker, freq, curr_date)

        return data_cashflow

    @staticmethod
    @tool
    # 获取 Simfin 收入报表
    def get_simfin_income_stmt(
        ticker: Annotated[str, "公司的股票代码"],
        freq: Annotated[
            str,
            "公司财务历史的报告频率：年度/季度",
        ],
        curr_date: Annotated[str, "您正在交易的当前日期，格式为yyyy-mm-dd"],
    ):
        """
        检索公司最新的收入报表
        Args:
            ticker (str): 公司的股票代码
            freq (str): 公司财务历史的报告频率：年度/季度
            curr_date (str): 您正在交易的当前日期，格式为yyyy-mm-dd
        Returns:
                str: 公司最新收入报表的报告
        """

        data_income_stmt = interface.get_simfin_income_statements(
            ticker, freq, curr_date
        )

        return data_income_stmt

    @staticmethod
    @tool
    # 获取 Google 新闻
    def get_google_news(
        query: Annotated[str, "搜索查询"],
        curr_date: Annotated[str, "当前日期，格式为yyyy-mm-dd"],
    ):
        """
        根据查询和日期范围从Google News检索最新新闻。
        Args:
            query (str): 搜索查询
            curr_date (str): 当前日期，格式为yyyy-mm-dd
            look_back_days (int): 回看多少天
        Returns:
            str: 包含基于查询和日期范围从Google News获取的最新新闻的格式化字符串。
        """

        google_news_results = interface.get_google_news(query, curr_date, 7)

        return google_news_results

    @staticmethod
    @tool
    # 使用 OpenAI 获取股票新闻
    def get_stock_news_openai(
        ticker: Annotated[str, "公司的股票代码"],
        curr_date: Annotated[str, "当前日期，格式为yyyy-mm-dd"],
    ):
        """
        使用OpenAI的新闻API检索关于给定股票的最新新闻。
        Args:
            ticker (str): 公司的股票代码。例如 AAPL, TSM
            curr_date (str): 当前日期，格式为yyyy-mm-dd
        Returns:
            str: 包含给定日期公司最新新闻的格式化字符串。
        """

        openai_news_results = interface.get_stock_news_openai(ticker, curr_date)

        return openai_news_results

    @staticmethod
    @tool
    # 使用 OpenAI 获取全球新闻
    def get_global_news_openai(
        curr_date: Annotated[str, "当前日期，格式为yyyy-mm-dd"],
    ):
        """
        使用OpenAI的宏观经济新闻API检索给定日期的最新宏观经济新闻。
        Args:
            curr_date (str): 当前日期，格式为yyyy-mm-dd
        Returns:
            str: 包含给定日期最新宏观经济新闻的格式化字符串。
        """

        openai_news_results = interface.get_global_news_openai(curr_date)

        return openai_news_results

    @staticmethod
    @tool
    # 使用 OpenAI 获取基本面信息
    def get_fundamentals_openai(
        ticker: Annotated[str, "公司的股票代码"],
        curr_date: Annotated[str, "当前日期，格式为yyyy-mm-dd"],
    ):
        """
        使用OpenAI的新闻API检索给定日期关于给定股票的最新基本面信息。
        Args:
            ticker (str): 公司的股票代码。例如 AAPL, TSM
            curr_date (str): 当前日期，格式为yyyy-mm-dd
        Returns:
            str: 包含给定日期公司最新基本面信息的格式化字符串。
        """

        openai_fundamentals_results = interface.get_fundamentals_openai(
            ticker, curr_date
        )

        return openai_fundamentals_results
