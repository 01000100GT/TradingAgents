# tradingagents/graph/conditional_logic.py
# 本文件包含处理条件逻辑的类，用于确定代理图的流程控制。

from tradingagents.agents.utils.agent_states import AgentState


# 条件逻辑类：处理确定图流程的条件逻辑。
class ConditionalLogic:
    """Handles conditional logic for determining graph flow."""

    # 初始化条件逻辑，设置最大辩论轮次和最大风险讨论轮次。
    def __init__(self, max_debate_rounds=1, max_risk_discuss_rounds=1):
        """Initialize with configuration parameters."""
        self.max_debate_rounds = max_debate_rounds
        self.max_risk_discuss_rounds = max_risk_discuss_rounds

    # 判断市场分析是否应继续。
    def should_continue_market(self, state: AgentState):
        """Determine if market analysis should continue."""
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools_market"
        return "Msg Clear Market"

    # 判断社交媒体分析是否应继续。
    def should_continue_social(self, state: AgentState):
        """Determine if social media analysis should continue."""
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools_social"
        return "Msg Clear Social"

    # 判断新闻分析是否应继续。
    def should_continue_news(self, state: AgentState):
        """Determine if news analysis should continue."""
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools_news"
        return "Msg Clear News"

    # 判断基本面分析是否应继续。
    def should_continue_fundamentals(self, state: AgentState):
        """Determine if fundamentals analysis should continue."""
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools_fundamentals"
        return "Msg Clear Fundamentals"

    # 判断投资辩论是否应继续。
    def should_continue_debate(self, state: AgentState) -> str:
        """Determine if debate should continue."""

        # 如果辩论轮次达到上限，则返回"Research Manager"
        if (
            state["investment_debate_state"]["count"] >= 2 * self.max_debate_rounds
        ):  # 2个代理之间进行3轮来回辩论
            return "Research Manager"
        # 如果当前响应以"Bull"开头，则返回"Bear Researcher"
        if state["investment_debate_state"]["current_response"].startswith("Bull"):
            return "Bear Researcher"
        # 否则返回"Bull Researcher"
        return "Bull Researcher"

    # 判断风险分析是否应继续。
    def should_continue_risk_analysis(self, state: AgentState) -> str:
        """Determine if risk analysis should continue."""
        # 如果风险讨论轮次达到上限，则返回"Risk Judge"
        if (
            state["risk_debate_state"]["count"] >= 3 * self.max_risk_discuss_rounds
        ):  # 3个代理之间进行3轮来回讨论
            return "Risk Judge"
        # 如果最新发言者是"Risky"，则返回"Safe Analyst"
        if state["risk_debate_state"]["latest_speaker"].startswith("Risky"):
            return "Safe Analyst"
        # 如果最新发言者是"Safe"，则返回"Neutral Analyst"
        if state["risk_debate_state"]["latest_speaker"].startswith("Safe"):
            return "Neutral Analyst"
        # 否则返回"Risky Analyst"
        return "Risky Analyst"
