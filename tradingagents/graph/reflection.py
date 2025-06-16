# tradingagents/graph/reflection.py
# 本文件包含处理决策反思和更新内存的类。

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from tradingagents.agents.utils.agent_utils import create_chat_openai


# 反思器类：处理决策反思和内存更新。
class Reflector:
    """Handles reflection on decisions and updating memory."""

    # 初始化反思器，传入一个快速思考的 LLM 或配置。
    def __init__(self, quick_thinking_llm_or_config, config=None):
        """Initialize the reflector with an LLM or config."""
        if isinstance(quick_thinking_llm_or_config, ChatOpenAI):
            self.quick_thinking_llm = quick_thinking_llm_or_config
        else:
            # 如果传入的是配置，则创建LLM实例
            config = quick_thinking_llm_or_config
            self.quick_thinking_llm = create_chat_openai(config, temperature=0.1)
        self.reflection_system_prompt = self._get_reflection_prompt()

    # 获取用于反思的系统提示。
    def _get_reflection_prompt(self) -> str:
        """Get the system prompt for reflection."""
        return """
你是一名专业的金融分析师，负责审查交易决策/分析，并提供全面的、分步的分析。
你的目标是提供对投资决策的详细见解，并突出改进机会，严格遵守以下准则：

1. 推理：
   - 对于每个交易决策，确定其是正确还是不正确。正确的决策会带来回报增加，而不正确的决策则相反。
   - 分析导致每次成功或错误的因素。考虑：
     - 市场情报。
     - 技术指标。
     - 技术信号。
     - 价格走势分析。
     - 整体市场数据分析
     - 新闻分析。
     - 社交媒体和情绪分析。
     - 基本面数据分析。
     - 权衡每个因素在决策过程中的重要性。

2. 改进：
   - 对于任何不正确的决策，提出修改建议以最大化回报。
   - 提供纠正措施或改进的详细列表，包括具体建议（例如，在特定日期将决策从持有更改为买入）。

3. 总结：
   - 总结从成功和错误中吸取的教训。
   - 强调如何将这些教训应用于未来的交易场景，并联系类似情况以应用所学知识。

4. 查询：
   - 将摘要中的关键见解提取为不超过 1000 个标记的简洁句子。
   - 确保精简后的句子捕捉到教训和推理的精髓，以便于参考。

严格遵守这些说明，并确保你的输出详细、准确且可操作。还将为你提供客观的市场描述，包括价格走势、技术指标、新闻和情绪，以便为你的分析提供更多上下文。
"""

    # 从状态中提取当前市场情况。
    def _extract_current_situation(self, current_state: Dict[str, Any]) -> str:
        """Extract the current market situation from the state."""
        curr_market_report = current_state["market_report"]
        curr_sentiment_report = current_state["sentiment_report"]
        curr_news_report = current_state["news_report"]
        curr_fundamentals_report = current_state["fundamentals_report"]

        return f"{curr_market_report}\n\n{curr_sentiment_report}\n\n{curr_news_report}\n\n{curr_fundamentals_report}"

    # 为特定组件生成反思。
    def _reflect_on_component(
        self, component_type: str, report: str, situation: str, returns_losses
    ) -> str:
        """Generate reflection for a component."""
        messages = [
            ("system", self.reflection_system_prompt),
            (
                "human",
                f"Returns: {returns_losses}\n\nAnalysis/Decision: {report}\n\nObjective Market Reports for Reference: {situation}",
            ),
        ]

        result = self.quick_thinking_llm.invoke(messages).content
        return result

    # 反思看涨研究员的分析并更新记忆。
    def reflect_bull_researcher(self, current_state, returns_losses, bull_memory):
        """Reflect on bull researcher's analysis and update memory."""
        situation = self._extract_current_situation(current_state)
        bull_debate_history = current_state["investment_debate_state"]["bull_history"]

        result = self._reflect_on_component(
            "BULL", bull_debate_history, situation, returns_losses
        )
        bull_memory.add_situations([(situation, result)])

    # 反思看跌研究员的分析并更新记忆。
    def reflect_bear_researcher(self, current_state, returns_losses, bear_memory):
        """Reflect on bear researcher's analysis and update memory."""
        situation = self._extract_current_situation(current_state)
        bear_debate_history = current_state["investment_debate_state"]["bear_history"]

        result = self._reflect_on_component(
            "BEAR", bear_debate_history, situation, returns_losses
        )
        bear_memory.add_situations([(situation, result)])

    # 反思交易员的决策并更新记忆。
    def reflect_trader(self, current_state, returns_losses, trader_memory):
        """Reflect on trader's decision and update memory."""
        situation = self._extract_current_situation(current_state)
        trader_decision = current_state["trader_investment_plan"]

        result = self._reflect_on_component(
            "TRADER", trader_decision, situation, returns_losses
        )
        trader_memory.add_situations([(situation, result)])

    # 反思投资判断者的决策并更新记忆。
    def reflect_invest_judge(self, current_state, returns_losses, invest_judge_memory):
        """Reflect on investment judge's decision and update memory."""
        situation = self._extract_current_situation(current_state)
        judge_decision = current_state["investment_debate_state"]["judge_decision"]

        result = self._reflect_on_component(
            "INVEST JUDGE", judge_decision, situation, returns_losses
        )
        invest_judge_memory.add_situations([(situation, result)])

    # 反思风险管理者的决策并更新记忆。
    def reflect_risk_manager(self, current_state, returns_losses, risk_manager_memory):
        """Reflect on risk manager's decision and update memory."""
        situation = self._extract_current_situation(current_state)
        judge_decision = current_state["risk_debate_state"]["judge_decision"]

        result = self._reflect_on_component(
            "RISK JUDGE", judge_decision, situation, returns_losses
        )
        risk_manager_memory.add_situations([(situation, result)])
