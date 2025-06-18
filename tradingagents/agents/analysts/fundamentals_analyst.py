# 这个文件定义了基本面分析师，负责收集和分析公司的基本面信息。
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


# 创建基本面分析师的节点
def create_fundamentals_analyst(llm, toolkit):
    # 基本面分析师节点函数
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [toolkit.get_fundamentals_openai]
        else:
            tools = [
                toolkit.get_finnhub_company_insider_sentiment,
                toolkit.get_finnhub_company_insider_transactions,
                toolkit.get_simfin_balance_sheet,
                toolkit.get_simfin_cashflow,
                toolkit.get_simfin_income_stmt,
            ]

        # 系统消息，定义分析师的角色和任务
        system_message = (
            "您是一位研究员，负责分析公司过去一周的基本面信息。请撰写一份关于公司基本面信息的综合报告，包括财务文件、公司概况、基本财务数据、公司财务历史、内部人士情绪和内部人士交易等，以全面了解公司的基本面信息，为交易员提供决策依据。请务必包含尽可能详细的信息。不要简单地说趋势混合，而是提供详细和细致的分析和见解，帮助交易员做出决策。"
            + " 请确保在报告末尾附上一个Markdown表格来整理报告中的要点，使其组织清晰、易于阅读。",
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
            "fundamentals_report": result.content,
        }

    return fundamentals_analyst_node
