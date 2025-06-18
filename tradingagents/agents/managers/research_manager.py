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
        prompt = f"""作为投资组合经理和辩论主持人，您的职责是批判性地评估这轮辩论并做出明确决策：支持空头分析师、多头分析师，或者只有在基于所提出论点有强力支持的情况下才选择持有。

简洁地总结双方的关键观点，重点关注最有说服力的证据或推理。您的建议——买入、卖出或持有——必须明确且可执行。避免仅仅因为双方都有合理观点就默认选择持有；要基于辩论中最有力的论点做出承诺。

此外，为交易员制定详细的投资计划。这应该包括：

您的建议：基于最有说服力论点的果断立场。
理由：解释为什么这些论点导致您的结论。
战略行动：实施建议的具体步骤。

考虑您在类似情况下的过往错误。利用这些见解来完善您的决策过程，确保您在学习和改进。以对话方式呈现您的分析，如同自然交谈，不使用特殊格式。

以下是您对过往错误的反思：
\"{past_memory_str}\"

以下是辩论内容：
辩论历史：
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
