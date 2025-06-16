# research_manager.py
# 本文件包含研究经理节点的功能，用于在投资辩论中做出决策并生成投资计划。

import time
import json


def create_research_manager(llm, memory):
    # research_manager_node 函数是研究经理节点的核心逻辑。
    # 它评估市场报告、情绪报告、新闻报告和基本面报告，
    # 结合过去的记忆，生成投资建议和详细的投资计划。
    def research_manager_node(state) -> dict:
        # history: 投资辩论的历史记录。
        history = state["investment_debate_state"].get("history", "")
        # market_research_report: 市场研究报告。
        market_research_report = state["market_report"]
        # sentiment_report: 情绪报告。
        sentiment_report = state["sentiment_report"]
        # news_report: 新闻报告。
        news_report = state["news_report"]
        # fundamentals_report: 基本面报告。
        fundamentals_report = state["fundamentals_report"]

        # investment_debate_state: 当前投资辩论的状态。
        investment_debate_state = state["investment_debate_state"]

        # curr_situation: 当前情况的汇总字符串，用于获取相关记忆。
        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        # past_memories: 根据当前情况从记忆中检索到的相关历史记忆。
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        # past_memory_str: 格式化后的历史记忆字符串，用于添加到提示中。
        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        # prompt: 发送给语言模型的提示，包含辩论历史和过去的记忆，
        # 以便语言模型做出投资决策并生成计划。
        prompt = f"""As the portfolio manager and debate facilitator, your role is to critically evaluate this round of debate and make a definitive decision: align with the bear analyst, the bull analyst, or choose Hold only if it is strongly justified based on the arguments presented.

Summarize the key points from both sides concisely, focusing on the most compelling evidence or reasoning. Your recommendation—Buy, Sell, or Hold—must be clear and actionable. Avoid defaulting to Hold simply because both sides have valid points; commit to a stance grounded in the debate's strongest arguments.

Additionally, develop a detailed investment plan for the trader. This should include:

Your Recommendation: A decisive stance supported by the most convincing arguments.
Rationale: An explanation of why these arguments lead to your conclusion.
Strategic Actions: Concrete steps for implementing the recommendation.
Take into account your past mistakes on similar situations. Use these insights to refine your decision-making and ensure you are learning and improving. Present your analysis conversationally, as if speaking naturally, without special formatting. 

Here are your past reflections on mistakes:
\"{past_memory_str}\"

Here is the debate:
Debate History:
{history}"""
        # response: 语言模型根据提示生成的响应。
        response = llm.invoke(prompt)

        # new_investment_debate_state: 更新后的投资辩论状态，包含裁判的决定。
        new_investment_debate_state = {
            "judge_decision": response.content,
            "history": investment_debate_state.get("history", ""),
            "bear_history": investment_debate_state.get("bear_history", ""),
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": response.content,
            "count": investment_debate_state["count"],
        }

        # 返回更新后的投资辩论状态和投资计划。
        return {
            "investment_debate_state": new_investment_debate_state,
            "investment_plan": response.content,
        }

    # 返回研究经理节点函数。
    return research_manager_node
