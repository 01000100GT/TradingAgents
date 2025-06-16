# 该文件定义了中立风险分析师（Neutral Debator）的角色，
# 负责在风险辩论中提供平衡的视角，权衡交易员决策或计划的潜在收益和风险。
# 它优先采用全面的方法，评估优缺点，同时考虑更广泛的市场趋势、潜在的经济变化和多元化策略。
import time
import json


# 创建中立风险分析师节点，用于在风险辩论中提出中立观点。
# 该节点负责处理辩论状态，生成基于现有市场数据的中立响应，并更新辩论历史。
def create_neutral_debator(llm):
    # 中立风险分析师节点的核心逻辑。
    # 它接收当前状态（包括风险辩论状态、各种市场报告和交易员的投资计划），
    # 生成一个中立论点，并更新辩论状态以反映新的论点。
    def neutral_node(state) -> dict:
        # 从状态中获取风险辩论相关信息
        risk_debate_state = state["risk_debate_state"]
        # 获取历史辩论记录
        history = risk_debate_state.get("history", "")
        # 获取中立风险分析师自身的历史论点
        neutral_history = risk_debate_state.get("neutral_history", "")

        # 获取当前辩论中激进分析师的最后回应
        current_risky_response = risk_debate_state.get("current_risky_response", "")
        # 获取当前辩论中保守分析师的最后回应
        current_safe_response = risk_debate_state.get("current_safe_response", "")

        # 市场研究报告
        market_research_report = state["market_report"]
        # 社交媒体情感报告
        sentiment_report = state["sentiment_report"]
        # 新闻报告
        news_report = state["news_report"]
        # 公司基本面报告
        fundamentals_report = state["fundamentals_report"]

        # 交易员的投资计划
        trader_decision = state["trader_investment_plan"]

        # 构建给语言模型的提示，指导其生成中立论点
        prompt = f"""As the Neutral Risk Analyst, your role is to provide a balanced perspective, weighing both the potential benefits and risks of the trader\'s decision or plan. You prioritize a well-rounded approach, evaluating the upsides and downsides while factoring in broader market trends, potential economic shifts, and diversification strategies.Here is the trader\'s decision:

{trader_decision}

Your task is to challenge both the Risky and Safe Analysts, pointing out where each perspective may be overly optimistic or overly cautious. Use insights from the following data sources to support a moderate, sustainable strategy to adjust the trader\'s decision:

Market Research Report: {market_research_report}
Social Media Sentiment Report: {sentiment_report}
Latest World Affairs Report: {news_report}
Company Fundamentals Report: {fundamentals_report}
Here is the current conversation history: {history} Here is the last response from the risky analyst: {current_risky_response} Here is the last response from the safe analyst: {current_safe_response}. If there are no responses from the other viewpoints, do not halluncinate and just present your point.

Engage actively by analyzing both sides critically, addressing weaknesses in the risky and conservative arguments to advocate for a more balanced approach. Challenge each of their points to illustrate why a moderate risk strategy might offer the best of both worlds, providing growth potential while safeguarding against extreme volatility. Focus on debating rather than simply presenting data, aiming to show that a balanced view can lead to the most reliable outcomes. Output conversationally as if you are speaking without any special formatting."""

        # 调用语言模型生成回应
        response = llm.invoke(prompt)

        # 格式化中立风险分析师的论点
        argument = f"Neutral Analyst: {response.content}"

        # 更新风险辩论状态
        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": neutral_history + "\n" + argument,
            "latest_speaker": "Neutral",
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": argument,
            "count": risk_debate_state["count"] + 1,
        }

        # 返回更新后的状态
        return {"risk_debate_state": new_risk_debate_state}

    # 返回中立风险分析师节点函数
    return neutral_node
