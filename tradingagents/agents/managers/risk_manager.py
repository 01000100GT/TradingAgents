# risk_manager.py
# 本文件包含风险经理节点的功能，用于在风险辩论中做出最终交易决策。

import time
import json


def create_risk_manager(llm, memory):
    # risk_manager_node 函数是风险经理节点的核心逻辑。
    # 它评估风险分析师的辩论，结合市场报告、新闻报告、基本面报告和情绪报告，
    # 并利用过去的记忆，生成最终的交易决策。
    def risk_manager_node(state) -> dict:

        # company_name: 感兴趣的公司名称。
        company_name = state["company_of_interest"]

        # history: 风险辩论的历史记录。
        history = state["risk_debate_state"]["history"]
        # risk_debate_state: 当前风险辩论的状态。
        risk_debate_state = state["risk_debate_state"]
        # market_research_report: 市场研究报告。
        market_research_report = state["market_report"]
        # news_report: 新闻报告。
        news_report = state["news_report"]
        # fundamentals_report: 基本面报告。
        fundamentals_report = state["news_report"]
        # sentiment_report: 情绪报告。
        sentiment_report = state["sentiment_report"]
        # trader_plan: 交易员的投资计划。
        trader_plan = state["investment_plan"]

        # curr_situation: 当前情况的汇总字符串，用于获取相关记忆。
        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        # past_memories: 根据当前情况从记忆中检索到的相关历史记忆。
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        # past_memory_str: 格式化后的历史记忆字符串，用于添加到提示中。
        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        # prompt: 发送给语言模型的提示，包含辩论历史、交易员计划和过去的记忆，
        # 以便语言模型做出最终的交易决策。
        prompt = f"""作为风险管理裁判和辩论主持人，您的目标是评估三位风险分析师——激进派、中性派和保守派——之间的辩论，并为交易员确定最佳行动方案。您的决策必须产生明确的建议：买入、卖出或持有。只有在有具体论据强力支持的情况下才选择持有，而不是在所有观点都看似合理时的默认选择。力求清晰和果断。

决策指导原则：
1. **总结关键论点**：从每位分析师那里提取最有力的观点，重点关注与当前情况的相关性。
2. **提供理由**：用辩论中的直接引用和反驳论点来支持您的建议。
3. **完善交易员计划**：从交易员的原始计划**{trader_plan}**开始，根据分析师的见解进行调整。
4. **从过去的错误中学习**：利用**{past_memory_str}**中的经验教训来解决之前的错误判断，改进您现在做出的决策，确保不会做出错误的买入/卖出/持有决定而造成损失。

交付成果：
- 明确可行的建议：买入、卖出或持有。
- 基于辩论和过去反思的详细推理。

---

**分析师辩论历史：**  
{history}

---

专注于可行的见解和持续改进。建立在过去经验的基础上，批判性地评估所有观点，确保每个决策都能推动更好的结果。"""

        # response: 语言模型根据提示生成的响应。
        response = llm.invoke(prompt)

        # new_risk_debate_state: 更新后的风险辩论状态，包含裁判的决定。
        new_risk_debate_state = {
            "judge_decision": response.content,
            "history": risk_debate_state["history"],
            "risky_history": risk_debate_state["risky_history"],
            "safe_history": risk_debate_state["safe_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "Judge",
            "current_risky_response": risk_debate_state["current_risky_response"],
            "current_safe_response": risk_debate_state["current_safe_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
        }

        # 返回更新后的风险辩论状态和最终交易决策。
        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": response.content,
        }

    # 返回风险经理节点函数。
    return risk_manager_node
