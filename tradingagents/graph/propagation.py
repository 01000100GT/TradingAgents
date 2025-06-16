# tradingagents/graph/propagation.py
# 本文件包含处理代理图状态初始化和传播的类。

from typing import Dict, Any
from tradingagents.agents.utils.agent_states import (
    AgentState,
    InvestDebateState,
    RiskDebateState,
)


# 传播器类：处理图中的状态初始化和传播。
class Propagator:
    """Handles state initialization and propagation through the graph."""

    # 初始化传播器，设置最大递归限制。
    def __init__(self, max_recur_limit=100):
        """Initialize with configuration parameters."""
        self.max_recur_limit = max_recur_limit

    # 为代理图创建初始状态。
    def create_initial_state(
        self, company_name: str, trade_date: str
    ) -> Dict[str, Any]:
        """Create the initial state for the agent graph."""
        return {
            "messages": [("human", company_name)],
            "company_of_interest": company_name,
            "trade_date": str(trade_date),
            # 投资辩论状态，包含历史记录、当前响应和计数。
            "investment_debate_state": InvestDebateState(
                {"history": "", "current_response": "", "count": 0}
            ),
            # 风险辩论状态，包含历史记录、不同风险响应和计数。
            "risk_debate_state": RiskDebateState(
                {
                    "history": "",
                    "current_risky_response": "",
                    "current_safe_response": "",
                    "current_neutral_response": "",
                    "count": 0,
                }
            ),
            "market_report": "",  # 市场报告
            "fundamentals_report": "",  # 基本面报告
            "sentiment_report": "",  # 情绪报告
            "news_report": "",  # 新闻报告
        }

    # 获取图调用的参数。
    def get_graph_args(self) -> Dict[str, Any]:
        """Get arguments for the graph invocation."""
        return {
            "stream_mode": "values",  # 流模式设置为"values"
            "config": {"recursion_limit": self.max_recur_limit},  # 配置递归限制
        }
