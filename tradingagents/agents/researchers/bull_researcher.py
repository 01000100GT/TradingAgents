# 该文件定义了牛市研究员（Bull Researcher）的角色，
# 负责在投资辩论中提出看涨观点，强调增长潜力、竞争优势和积极的市场指标。
# 它利用各种市场报告和历史辩论数据来构建有说服力的论点。
from langchain_core.messages import AIMessage
import time
import json


# 创建牛市研究员节点，用于在投资辩论中提出看涨论点。
# 该节点负责处理辩论状态，生成基于现有市场数据的看涨响应，并更新辩论历史。
def create_bull_researcher(llm, memory):
    # 牛市研究员节点的核心逻辑。
    # 它接收当前状态（包括投资辩论状态、各种市场报告），
    # 生成一个看涨论点，并更新辩论状态以反映新的论点。
    def bull_node(state) -> dict:
        # 从状态中获取投资辩论相关信息
        investment_debate_state = state["investment_debate_state"]
        # 获取历史辩论记录
        history = investment_debate_state.get("history", "")
        # 获取牛市研究员自身的历史论点
        bull_history = investment_debate_state.get("bull_history", "")

        # 获取当前辩论中对方（熊市研究员）的最后回应
        current_response = investment_debate_state.get("current_response", "")
        # 市场研究报告
        market_research_report = state["market_report"]
        # 社交媒体情感报告
        sentiment_report = state["sentiment_report"]
        # 新闻报告
        news_report = state["news_report"]
        # 公司基本面报告
        fundamentals_report = state["fundamentals_report"]

        # 结合所有当前情况报告，用于记忆检索
        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        # 从记忆中获取与当前情况相关的过往经验
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        # 格式化过往记忆为字符串
        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        # 构建给语言模型的提示，指导其生成看涨论点
        prompt = f"""You are a Bull Analyst advocating for investing in the stock. Your task is to build a strong, evidence-based case emphasizing growth potential, competitive advantages, and positive market indicators. Leverage the provided research and data to address concerns and counter bearish arguments effectively.

Key points to focus on:
- Growth Potential: Highlight the company\'s market opportunities, revenue projections, and scalability.
- Competitive Advantages: Emphasize factors like unique products, strong branding, or dominant market positioning.
- Positive Indicators: Use financial health, industry trends, and recent positive news as evidence.
- Bear Counterpoints: Critically analyze the bear argument with specific data and sound reasoning, addressing concerns thoroughly and showing why the bull perspective holds stronger merit.
- Engagement: Present your argument in a conversational style, engaging directly with the bear analyst\'s points and debating effectively rather than just listing data.

Resources available:
Market research report: {market_research_report}
Social media sentiment report: {sentiment_report}
Latest world affairs news: {news_report}
Company fundamentals report: {fundamentals_report}
Conversation history of the debate: {history}
Last bear argument: {current_response}
Reflections from similar situations and lessons learned: {past_memory_str}
Use this information to deliver a compelling bull argument, refute the bear\'s concerns, and engage in a dynamic debate that demonstrates the strengths of the bull position. You must also address reflections and learn from lessons and mistakes you made in the past.
"""

        # 调用语言模型生成回应
        response = llm.invoke(prompt)

        # 格式化牛市研究员的论点
        argument = f"Bull Analyst: {response.content}"

        # 更新投资辩论状态
        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        # 返回更新后的状态
        return {"investment_debate_state": new_investment_debate_state}

    # 返回牛市研究员节点函数
    return bull_node
