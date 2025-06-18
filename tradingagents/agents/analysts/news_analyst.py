# 这个文件定义了新闻分析师，负责分析近期新闻和市场趋势。
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


# 创建新闻分析师的节点
def create_news_analyst(llm, toolkit):
    # 新闻分析师节点函数
    def news_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [toolkit.get_global_news_openai, toolkit.get_google_news]
        else:
            tools = [
                toolkit.get_finnhub_news,
                toolkit.get_reddit_news,
                toolkit.get_google_news,
            ]

        # 系统消息，定义分析师的角色和任务
        system_message = (
            "您是一位新闻研究员，负责分析过去一周的近期新闻和趋势。请撰写一份关于当前世界状况的综合报告，该报告与交易和宏观经济学相关。查看来自EODHD和finnhub的新闻以确保全面性。不要简单地说趋势混合，而是提供详细和细致的分析和见解，帮助交易员做出决策。"
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
                    "供您参考，当前日期是{current_date}。我们正在分析的公司是{ticker}",
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
            "news_report": result.content,
        }

    return news_analyst_node
