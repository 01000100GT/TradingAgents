# 该文件定义了激进风险分析师（Aggressive Debator）的角色，
# 负责在风险辩论中倡导高回报、高风险的投资机会，并强调大胆的策略和竞争优势。
# 它利用市场数据和情绪分析来加强论点，并反驳保守派和中立派的观点。
import time
import json


# 创建激进风险分析师节点，用于在风险辩论中提出激进观点。
# 该节点负责处理辩论状态，生成基于现有市场数据的激进响应，并更新辩论历史。
def create_risky_debator(llm):
    # 激进风险分析师节点的核心逻辑。
    # 它接收当前状态（包括风险辩论状态、各种市场报告和交易员的投资计划），
    # 生成一个激进论点，并更新辩论状态以反映新的论点。
    def risky_node(state) -> dict:
        # 从状态中获取风险辩论相关信息
        risk_debate_state = state["risk_debate_state"]
        # 获取历史辩论记录
        history = risk_debate_state.get("history", "")
        # 获取激进风险分析师自身的历史论点
        risky_history = risk_debate_state.get("risky_history", "")

        # 获取当前辩论中保守分析师的最后回应
        current_safe_response = risk_debate_state.get("current_safe_response", "")
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

        # 构建给语言模型的提示，指导其生成激进论点
        prompt = f"""作为激进风险分析师，你的角色是积极支持高回报、高风险的机会，强调大胆的策略和竞争优势。在评估交易员的决策或计划时，专注于潜在的上升空间、增长潜力和创新收益——即使这些伴随着较高的风险。使用提供的市场数据和情感分析来加强你的论点并挑战对立观点。具体地，直接回应保守和中立分析师提出的每一点，用数据驱动的反驳和有说服力的推理进行反击。突出他们的谨慎态度可能错过关键机会的地方，或者他们的假设可能过于保守的地方。以下是交易员的决策：

{trader_decision}

你的任务是通过质疑和批评保守和中立立场来为交易员的决策创建一个令人信服的案例，以证明为什么你的高回报视角提供了最佳的前进道路。将以下来源的见解纳入你的论点中：

市场研究报告：{market_research_report}
社交媒体情感报告：{sentiment_report}
最新国际时事报告：{news_report}
公司基本面报告：{fundamentals_report}
以下是当前对话历史：{history} 以下是保守分析师的最后论点：{current_safe_response} 以下是中立分析师的最后论点：{current_neutral_response}。如果没有来自其他观点的回应，不要虚构，只需呈现你的观点。

积极参与，通过解决任何提出的具体担忧，反驳他们逻辑中的弱点，并断言承担风险以超越市场常规的好处。保持专注于辩论和说服，而不仅仅是呈现数据。挑战每个反驳点，以强调为什么高风险方法是最优的。以对话方式输出，就像你在说话一样，不需要任何特殊格式。"""

        # 调用语言模型生成回应
        response = llm.invoke(prompt)

        # 格式化激进风险分析师的论点
        argument = f"Risky Analyst: {response.content}"

        # 更新风险辩论状态
        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risky_history + "\n" + argument,
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Risky",
            "current_risky_response": argument,
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        # 返回更新后的状态
        return {"risk_debate_state": new_risk_debate_state}

    # 返回激进风险分析师节点函数
    return risky_node
