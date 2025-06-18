from langchain_core.messages import AIMessage
import time
import json


# 该文件定义了熊市研究员（Bear Researcher）的角色，
# 负责在投资辩论中提出看跌观点，强调风险、挑战和消极的市场指标。
# 它利用各种市场报告和历史辩论数据来构建有说服力的论点。


# 创建熊市研究员节点，用于在投资辩论中提出看跌论点。
# 该节点负责处理辩论状态，生成基于现有市场数据的看跌响应，并更新辩论历史。
def create_bear_researcher(llm, memory):
    # 熊市研究员节点的核心逻辑。
    # 它接收当前状态（包括投资辩论状态、各种市场报告），
    # 生成一个看跌论点，并更新辩论状态以反映新的论点。
    def bear_node(state) -> dict:
        # 从状态中获取投资辩论相关信息
        investment_debate_state = state["investment_debate_state"]
        # 获取历史辩论记录
        history = investment_debate_state.get("history", "")
        # 获取熊市研究员自身的历史论点
        bear_history = investment_debate_state.get("bear_history", "")

        # 获取当前辩论中对方（牛市研究员）的最后回应
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

        # 构建给语言模型的提示，指导其生成看跌论点
        prompt = f"""你是一位熊市分析师，负责提出反对投资该股票的论点。你的目标是提出一个深思熟虑的论点，强调风险、挑战和负面指标。利用提供的研究和数据来突出潜在的不利因素，并有效地反驳看涨论点。

重点关注要点：

- 风险与挑战：突出可能阻碍股票表现的因素，如市场饱和、财务不稳定或宏观经济威胁。
- 竞争劣势：强调弱点，如较弱的市场定位、创新能力下降或来自竞争对手的威胁。
- 负面指标：利用财务数据、市场趋势或最近不利新闻的证据来支持你的立场。
- 反驳看涨观点：用具体数据和合理推理批判性地分析看涨论点，揭露弱点或过度乐观的假设。
- 参与讨论：以对话式风格呈现你的论点，直接回应牛市分析师的观点并有效辩论，而不是简单地列举事实。

可用资源：

市场研究报告：{market_research_report}
社交媒体情感报告：{sentiment_report}
最新国际时事新闻：{news_report}
公司基本面报告：{fundamentals_report}
辩论历史记录：{history}
最后的看涨论点：{current_response}
类似情况的反思和经验教训：{past_memory_str}
使用这些信息提出令人信服的看跌论点，反驳看涨观点的声明，并参与动态辩论，展示投资该股票的风险和弱点。你还必须处理反思，并从过去的经验教训和错误中学习。
"""

        # 调用语言模型生成回应
        response = llm.invoke(prompt)

        # 格式化熊市研究员的论点
        argument = f"Bear Analyst: {response.content}"

        # 更新投资辩论状态
        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        # 返回更新后的状态
        return {"investment_debate_state": new_investment_debate_state}

    # 返回熊市研究员节点函数
    return bear_node
