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
        prompt = f"""作为中立风险分析师，你的角色是提供平衡的视角，权衡交易员决策或计划的潜在收益和风险。你优先采用全面的方法，评估优缺点，同时考虑更广泛的市场趋势、潜在的经济变化和多元化策略。以下是交易员的决策：

{trader_decision}

你的任务是挑战激进和安全分析师，指出每种观点可能过于乐观或过于谨慎的地方。使用以下数据来源的见解来支持调整交易员决策的温和、可持续策略：

市场研究报告：{market_research_report}
社交媒体情感报告：{sentiment_report}
最新国际时事报告：{news_report}
公司基本面报告：{fundamentals_report}
以下是当前对话历史：{history} 以下是激进分析师的最后回应：{current_risky_response} 以下是安全分析师的最后回应：{current_safe_response}。如果没有来自其他观点的回应，不要虚构，只需呈现你的观点。

通过批判性地分析双方，解决激进和保守论点中的弱点，积极参与讨论，以倡导更平衡的方法。挑战他们的每个观点，以说明为什么温和的风险策略可能提供两全其美的效果，既提供增长潜力又防范极端波动。专注于辩论而不是简单地呈现数据，旨在表明平衡的观点可以带来最可靠的结果。以对话方式输出，就像你在说话一样，不需要任何特殊格式。"""

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
