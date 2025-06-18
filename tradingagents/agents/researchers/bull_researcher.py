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
        prompt = f"""你是一位牛市分析师，倡导投资该股票。你的任务是建立一个强有力的、基于证据的论证，强调增长潜力、竞争优势和积极的市场指标。利用提供的研究和数据来解决担忧并有效地反驳看跌论点。

重点关注要点：
- 增长潜力：突出公司的市场机会、收入预测和可扩展性。
- 竞争优势：强调独特产品、强势品牌或主导市场地位等因素。
- 积极指标：利用财务健康状况、行业趋势和最近的正面新闻作为证据。
- 反驳看跌观点：用具体数据和合理推理批判性地分析看跌论点，彻底解决担忧并说明为什么看涨观点具有更强的价值。
- 参与讨论：以对话式风格呈现你的论点，直接回应熊市分析师的观点并有效辩论，而不是仅仅列举数据。

可用资源：
市场研究报告：{market_research_report}
社交媒体情感报告：{sentiment_report}
最新国际时事新闻：{news_report}
公司基本面报告：{fundamentals_report}
辩论历史记录：{history}
最后的看跌论点：{current_response}
类似情况的反思和经验教训：{past_memory_str}
使用这些信息提出令人信服的看涨论点，反驳看跌观点的担忧，并参与动态辩论，展示看涨立场的优势。你还必须处理反思，并从过去的经验教训和错误中学习。
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
