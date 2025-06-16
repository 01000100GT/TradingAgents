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
        prompt = f"""As the Risk Management Judge and Debate Facilitator, your goal is to evaluate the debate between three risk analysts—Risky, Neutral, and Safe/Conservative—and determine the best course of action for the trader. Your decision must result in a clear recommendation: Buy, Sell, or Hold. Choose Hold only if strongly justified by specific arguments, not as a fallback when all sides seem valid. Strive for clarity and decisiveness.

Guidelines for Decision-Making:
1. **Summarize Key Arguments**: Extract the strongest points from each analyst, focusing on relevance to the context.
2. **Provide Rationale**: Support your recommendation with direct quotes and counterarguments from the debate.
3. **Refine the Trader's Plan**: Start with the trader's original plan, **{trader_plan}**, and adjust it based on the analysts' insights.
4. **Learn from Past Mistakes**: Use lessons from **{past_memory_str}** to address prior misjudgments and improve the decision you are making now to make sure you don't make a wrong BUY/SELL/HOLD call that loses money.

Deliverables:
- A clear and actionable recommendation: Buy, Sell, or Hold.
- Detailed reasoning anchored in the debate and past reflections.

---

**Analysts Debate History:**  
{history}

---

Focus on actionable insights and continuous improvement. Build on past lessons, critically evaluate all perspectives, and ensure each decision advances better outcomes."""

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
