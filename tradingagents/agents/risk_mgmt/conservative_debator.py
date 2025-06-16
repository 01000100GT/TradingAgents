# 该文件定义了保守风险分析师（Conservative Debator）的角色，
# 负责在风险辩论中优先保护资产，最小化波动性，并确保稳定、可靠的增长。
# 它仔细评估潜在损失、经济衰退和市场波动。
from langchain_core.messages import AIMessage
import time
import json


# 创建保守风险分析师节点，用于在风险辩论中提出保守观点。
# 该节点负责处理辩论状态，生成基于现有市场数据的保守响应，并更新辩论历史。
def create_safe_debator(llm):
    # 保守风险分析师节点的核心逻辑。
    # 它接收当前状态（包括风险辩论状态、各种市场报告和交易员的投资计划），
    # 生成一个保守论点，并更新辩论状态以反映新的论点。
    def safe_node(state) -> dict:
        # 从状态中获取风险辩论相关信息
        risk_debate_state = state["risk_debate_state"]
        # 获取历史辩论记录
        history = risk_debate_state.get("history", "")
        # 获取保守风险分析师自身的历史论点
        safe_history = risk_debate_state.get("safe_history", "")

        # 获取当前辩论中激进分析师的最后回应
        current_risky_response = risk_debate_state.get("current_risky_response", "")
        # 获取当前辩论中中立分析师的最后回应
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

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

        # 构建给语言模型的提示，指导其生成保守论点
        prompt = f"""As the Safe/Conservative Risk Analyst, your primary objective is to protect assets, minimize volatility, and ensure steady, reliable growth. You prioritize stability, security, and risk mitigation, carefully assessing potential losses, economic downturns, and market volatility. When evaluating the trader\'s decision or plan, critically examine high-risk elements, pointing out where the decision may expose the firm to undue risk and where more cautious alternatives could secure long-term gains. Here is the trader\'s decision:

{trader_decision}

Your task is to actively counter the arguments of the Risky and Neutral Analysts, highlighting where their views may overlook potential threats or fail to prioritize sustainability. Respond directly to their points, drawing from the following data sources to build a convincing case for a low-risk approach adjustment to the trader\'s decision:

Market Research Report: {market_research_report}
Social Media Sentiment Report: {sentiment_report}
Latest World Affairs Report: {news_report}
Company Fundamentals Report: {fundamentals_report}
Here is the current conversation history: {history} Here is the last response from the risky analyst: {current_risky_response} Here is the last response from the neutral analyst: {current_neutral_response}. If there are no responses from the other viewpoints, do not halluncinate and just present your point.

Engage by questioning their optimism and emphasizing the potential downsides they may have overlooked. Address each of their counterpoints to showcase why a conservative stance is ultimately the safest path for the firm\'s assets. Focus on debating and critiquing their arguments to demonstrate the strength of a low-risk strategy over their approaches. Output conversationally as if you are speaking without any special formatting."""

        # 调用语言模型生成回应
        response = llm.invoke(prompt)

        # 格式化保守风险分析师的论点
        argument = f"Safe Analyst: {response.content}"

        # 更新风险辩论状态
        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": safe_history + "\n" + argument,
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Safe",
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": argument,
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        # 返回更新后的状态
        return {"risk_debate_state": new_risk_debate_state}

    # 返回保守风险分析师节点函数
    return safe_node
