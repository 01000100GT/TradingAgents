# TradingAgents/graph/signal_processing.py
# 该文件负责处理交易信号，提取可操作的决策。

from langchain_openai import ChatOpenAI


class SignalProcessor:
    """
    信号处理器
    处理交易信号以提取可操作的决策。
    Processes trading signals to extract actionable decisions.
    """

    def __init__(self, quick_thinking_llm: ChatOpenAI):
        """
        使用LLM进行处理初始化。
        Initialize with an LLM for processing.
        """
        # quick_thinking_llm: 快速思考LLM
        self.quick_thinking_llm = quick_thinking_llm

    def process_signal(self, full_signal: str) -> str:
        """
        处理完整的交易信号以提取核心决策。
        Process a full trading signal to extract the core decision.

        Args:
            full_signal: 完整的交易信号文本
                         Complete trading signal text

        Returns:
            提取的决策（BUY、SELL或HOLD）
            Extracted decision (BUY, SELL, or HOLD)
        """
        # messages: 消息列表
        messages = [
            (
                "system",
                "You are an efficient assistant designed to analyze paragraphs or financial reports provided by a group of analysts. Your task is to extract the investment decision: SELL, BUY, or HOLD. Provide only the extracted decision (SELL, BUY, or HOLD) as your output, without adding any additional text or information.",
            ),
            ("human", full_signal),
        ]

        return self.quick_thinking_llm.invoke(messages).content
