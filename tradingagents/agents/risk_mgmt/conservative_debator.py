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
        prompt = f"""作为安全/保守风险分析师，你的主要目标是保护资产，最小化波动性，并确保稳定、可靠的增长。你优先考虑稳定性、安全性和风险缓解，仔细评估潜在损失、经济衰退和市场波动。在评估交易员的决策或计划时，批判性地审查高风险要素，指出决策可能使公司面临不当风险的地方，以及更谨慎的替代方案可以确保长期收益的地方。以下是交易员的决策：

{trader_decision}

你的任务是积极反驳激进和中立分析师的论点，突出他们的观点可能忽视潜在威胁或未能优先考虑可持续性的地方。直接回应他们的观点，利用以下数据来源为交易员决策的低风险方法调整建立令人信服的案例：

市场研究报告：{market_research_report}
社交媒体情感报告：{sentiment_report}
最新国际时事报告：{news_report}
公司基本面报告：{fundamentals_report}
以下是当前对话历史：{history} 以下是激进分析师的最后回应：{current_risky_response} 以下是中立分析师的最后回应：{current_neutral_response}。如果没有来自其他观点的回应，不要虚构，只需呈现你的观点。

通过质疑他们的乐观态度并强调他们可能忽视的潜在不利因素来参与讨论。回应他们的每个反驳点，以展示为什么保守立场最终是公司资产最安全的道路。专注于辩论和批评他们的论点，以证明低风险策略相对于他们方法的优势。以对话方式输出，就像你在说话一样，不需要任何特殊格式。"""

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
