# 这个文件定义了市场分析师，负责分析金融市场和选择相关指标。
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


# 创建市场分析师的节点
def create_market_analyst(llm, toolkit):

    # 市场分析师节点函数
    def market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [
                toolkit.get_YFin_data_online,
                toolkit.get_stockstats_indicators_report_online,
            ]
        else:
            tools = [
                toolkit.get_YFin_data,
                toolkit.get_stockstats_indicators_report,
            ]

        # 系统消息，定义分析师的角色和任务
        system_message = (
            """您是一位交易助手，负责分析金融市场。您的职责是从以下列表中为给定的市场条件或交易策略选择**最相关的指标**。目标是选择最多**8个指标**，这些指标提供互补的见解而无冗余。类别及每个类别的指标如下：

移动平均线：
- close_50_sma: 50日简单移动平均线：中期趋势指标。用法：识别趋势方向并作为动态支撑/阻力。提示：滞后于价格；结合更快的指标获得及时信号。
- close_200_sma: 200日简单移动平均线：长期趋势基准。用法：确认整体市场趋势并识别黄金/死亡交叉设置。提示：反应缓慢；最适合战略趋势确认而非频繁交易入场。
- close_10_ema: 10日指数移动平均线：响应性短期平均线。用法：捕捉动量快速变化和潜在入场点。提示：在震荡市场中容易产生噪音；与较长平均线一起使用以过滤虚假信号。

MACD相关：
- macd: MACD：通过EMA差值计算动量。用法：寻找交叉和背离作为趋势变化信号。提示：在低波动或横盘市场中需与其他指标确认。
- macds: MACD信号线：MACD线的EMA平滑。用法：使用与MACD线的交叉来触发交易。提示：应作为更广泛策略的一部分以避免假阳性。
- macdh: MACD柱状图：显示MACD线与其信号线之间的差距。用法：可视化动量强度并早期发现背离。提示：可能波动较大；在快速变化的市场中需配合额外过滤器。

动量指标：
- rsi: RSI：测量动量以标记超买/超卖条件。用法：应用70/30阈值并观察背离来信号反转。提示：在强趋势中，RSI可能保持极值；始终与趋势分析交叉检查。

波动率指标：
- boll: 布林带中线：作为布林带基础的20日SMA。用法：作为价格运动的动态基准。提示：与上下轨结合使用以有效发现突破或反转。
- boll_ub: 布林带上轨：通常是中线上方2个标准差。用法：信号潜在超买条件和突破区域。提示：用其他工具确认信号；在强趋势中价格可能沿轨运行。
- boll_lb: 布林带下轨：通常是中线下方2个标准差。用法：指示潜在超卖条件。提示：使用额外分析避免虚假反转信号。
- atr: ATR：平均真实波幅以测量波动率。用法：根据当前市场波动率设置止损水平和调整仓位大小。提示：这是一个反应性指标，应作为更广泛风险管理策略的一部分使用。

基于成交量的指标：
- vwma: VWMA：按成交量加权的移动平均线。用法：通过整合价格行为和成交量数据来确认趋势。提示：注意成交量激增造成的偏差结果；与其他成交量分析结合使用。

- 选择提供多样化和互补信息的指标。避免冗余（例如，不要同时选择rsi和stochrsi）。还要简要解释为什么它们适合给定的市场环境。当您调用工具时，请使用上面提供的指标的确切名称，因为它们是定义的参数，否则您的调用将失败。请确保首先调用get_YFin_data来检索生成指标所需的CSV。撰写一份非常详细和细致的趋势观察报告。不要简单地说趋势混合，而是提供详细和细致的分析和见解，帮助交易员做出决策。"""
            + """ 请确保在报告末尾附上一个Markdown表格来整理报告中的要点，使其组织清晰、易于阅读。"""
        )

        # 创建聊天提示模板
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "您是一位有用的AI助手，与其他助手协作。"
                    " 使用提供的工具来回答问题。"
                    " 如果您无法完全回答，没关系；拥有不同工具的其他助手"
                    " 会在您停下的地方继续帮助。请尽力取得进展。"
                    " 如果您或任何其他助手有最终交易建议：**买入/持有/卖出**或可交付成果，"
                    " 请在回复前加上'最终交易建议：**买入/持有/卖出**'，以便团队知道何时停止。"
                    " 您可以使用以下工具：{tool_names}。\n{system_message}"
                    "供您参考，当前日期是{current_date}。我们要分析的公司是{ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        # 创建链
        chain = prompt | llm.bind_tools(tools)

        # 调用链获取结果
        result = chain.invoke(state["messages"])

        return {
            "messages": [result],
            "market_report": result.content,
        }

    return market_analyst_node
