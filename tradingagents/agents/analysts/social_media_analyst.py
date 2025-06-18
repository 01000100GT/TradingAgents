# 这个文件定义了社交媒体分析师，负责分析社交媒体帖子、公司新闻和公众情绪。
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json


# 创建社交媒体分析师的节点
def create_social_media_analyst(llm, toolkit):
    # 社交媒体分析师节点函数
    def social_media_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [toolkit.get_stock_news_openai]
        else:
            tools = [
                toolkit.get_reddit_stock_info,
            ]

        # 系统消息，定义分析师的角色和任务
        system_message = (
            "您是一位社交媒体和公司特定新闻研究员/分析师，负责分析过去一周特定公司的社交媒体帖子、近期公司新闻和公众情绪。您将获得一个公司的名称，您的目标是撰写一份综合性的详细报告，详述您的分析、见解以及对交易员和投资者的影响，内容涵盖该公司的当前状态，包括社交媒体分析、人们对公司的看法、分析人们每天对公司的情绪数据，以及查看近期公司新闻。尽量查看所有可能的来源，从社交媒体到情绪到新闻。不要简单地说趋势混合，而是提供详细和细致的分析和见解，帮助交易员做出决策。"
            + """ 请确保在报告末尾附上一个Markdown表格来整理报告中的要点，使其组织清晰、易于阅读。""",
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
                    "供您参考，当前日期是{current_date}。我们要分析的当前公司是{ticker}",
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
            "sentiment_report": result.content,
        }

    return social_media_analyst_node
