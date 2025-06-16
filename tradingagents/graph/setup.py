# TradingAgents/graph/setup.py
# 该文件负责设置和配置代理图（Agent Graph）。

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode

from tradingagents.agents import *
from tradingagents.agents.utils.agent_states import AgentState
from tradingagents.agents.utils.agent_utils import Toolkit

from .conditional_logic import ConditionalLogic


class GraphSetup:
    """
    图配置类
    处理代理图的设置和配置。
    Handles the setup and configuration of the agent graph.
    """

    def __init__(
        self,
        quick_thinking_llm: ChatOpenAI,
        deep_thinking_llm: ChatOpenAI,
        toolkit: Toolkit,
        tool_nodes: Dict[str, ToolNode],
        bull_memory,
        bear_memory,
        trader_memory,
        invest_judge_memory,
        risk_manager_memory,
        conditional_logic: ConditionalLogic,
    ):
        """
        初始化所需组件。
        Initialize with required components.
        """
        # quick_thinking_llm: 快速思考LLM
        self.quick_thinking_llm = quick_thinking_llm
        # deep_thinking_llm: 深度思考LLM
        self.deep_thinking_llm = deep_thinking_llm
        # toolkit: 工具包
        self.toolkit = toolkit
        # tool_nodes: 工具节点
        self.tool_nodes = tool_nodes
        # bull_memory: 看涨记忆
        self.bull_memory = bull_memory
        # bear_memory: 看跌记忆
        self.bear_memory = bear_memory
        # trader_memory: 交易员记忆
        self.trader_memory = trader_memory
        # invest_judge_memory: 投资判断记忆
        self.invest_judge_memory = invest_judge_memory
        # risk_manager_memory: 风险经理记忆
        self.risk_manager_memory = risk_manager_memory
        # conditional_logic: 条件逻辑
        self.conditional_logic = conditional_logic

    def setup_graph(
        self, selected_analysts=["market", "social", "news", "fundamentals"]
    ):
        """
        设置并编译代理工作流图。
        Set up and compile the agent workflow graph.

        Args:
            selected_analysts (list): 要包含的分析师类型列表。选项包括：
                                      List of analyst types to include. Options are:
                - "market": 市场分析师
                          Market analyst
                - "social": 社交媒体分析师
                          Social media analyst
                - "news": 新闻分析师
                        News analyst
                - "fundamentals": 基本面分析师
                                Fundamentals analyst
        """
        if len(selected_analysts) == 0:
            raise ValueError("Trading Agents Graph Setup Error: no analysts selected!")

        # Create analyst nodes
        # 创建分析师节点
        analyst_nodes = {}
        # delete_nodes: 删除节点
        delete_nodes = {}
        # tool_nodes: 工具节点
        tool_nodes = {}

        if "market" in selected_analysts:
            analyst_nodes["market"] = create_market_analyst(
                self.quick_thinking_llm, self.toolkit
            )
            delete_nodes["market"] = create_msg_delete()
            tool_nodes["market"] = self.tool_nodes["market"]

        if "social" in selected_analysts:
            analyst_nodes["social"] = create_social_media_analyst(
                self.quick_thinking_llm, self.toolkit
            )
            delete_nodes["social"] = create_msg_delete()
            tool_nodes["social"] = self.tool_nodes["social"]

        if "news" in selected_analysts:
            analyst_nodes["news"] = create_news_analyst(
                self.quick_thinking_llm, self.toolkit
            )
            delete_nodes["news"] = create_msg_delete()
            tool_nodes["news"] = self.tool_nodes["news"]

        if "fundamentals" in selected_analysts:
            analyst_nodes["fundamentals"] = create_fundamentals_analyst(
                self.quick_thinking_llm, self.toolkit
            )
            delete_nodes["fundamentals"] = create_msg_delete()
            tool_nodes["fundamentals"] = self.tool_nodes["fundamentals"]

        # Create researcher and manager nodes
        # 创建研究员和经理节点
        # bull_researcher_node: 看涨研究员节点
        bull_researcher_node = create_bull_researcher(
            self.quick_thinking_llm, self.bull_memory
        )
        # bear_researcher_node: 看跌研究员节点
        bear_researcher_node = create_bear_researcher(
            self.quick_thinking_llm, self.bear_memory
        )
        # research_manager_node: 研究经理节点
        research_manager_node = create_research_manager(
            self.deep_thinking_llm, self.invest_judge_memory
        )
        # trader_node: 交易员节点
        trader_node = create_trader(self.quick_thinking_llm, self.trader_memory)

        # Create risk analysis nodes
        # 创建风险分析节点
        # risky_analyst: 激进分析师
        risky_analyst = create_risky_debator(self.quick_thinking_llm)
        # neutral_analyst: 中立分析师
        neutral_analyst = create_neutral_debator(self.quick_thinking_llm)
        # safe_analyst: 保守分析师
        safe_analyst = create_safe_debator(self.quick_thinking_llm)
        # risk_manager_node: 风险经理节点
        risk_manager_node = create_risk_manager(
            self.deep_thinking_llm, self.risk_manager_memory
        )

        # Create workflow
        # 创建工作流
        # workflow: 工作流
        workflow = StateGraph(AgentState)

        # Add analyst nodes to the graph
        # 将分析师节点添加到图中
        for analyst_type, node in analyst_nodes.items():
            workflow.add_node(f"{analyst_type.capitalize()} Analyst", node)
            workflow.add_node(
                f"Msg Clear {analyst_type.capitalize()}", delete_nodes[analyst_type]
            )
            workflow.add_node(f"tools_{analyst_type}", tool_nodes[analyst_type])

        # Add other nodes
        # 添加其他节点
        workflow.add_node("Bull Researcher", bull_researcher_node)
        workflow.add_node("Bear Researcher", bear_researcher_node)
        workflow.add_node("Research Manager", research_manager_node)
        workflow.add_node("Trader", trader_node)
        workflow.add_node("Risky Analyst", risky_analyst)
        workflow.add_node("Neutral Analyst", neutral_analyst)
        workflow.add_node("Safe Analyst", safe_analyst)
        workflow.add_node("Risk Judge", risk_manager_node)

        # Define edges
        # 定义边
        # Start with the first analyst
        # 从第一个分析师开始
        first_analyst = selected_analysts[0]
        workflow.add_edge(START, f"{first_analyst.capitalize()} Analyst")

        # Connect analysts in sequence
        # 按顺序连接分析师
        for i, analyst_type in enumerate(selected_analysts):
            current_analyst = f"{analyst_type.capitalize()} Analyst"
            current_tools = f"tools_{analyst_type}"
            current_clear = f"Msg Clear {analyst_type.capitalize()}"

            # Add conditional edges for current analyst
            # 为当前分析师添加条件边
            workflow.add_conditional_edges(
                current_analyst,
                getattr(self.conditional_logic, f"should_continue_{analyst_type}"),
                [current_tools, current_clear],
            )
            workflow.add_edge(current_tools, current_analyst)

            # Connect to next analyst or to Bull Researcher if this is the last analyst
            # 连接到下一个分析师，如果这是最后一个分析师则连接到看涨研究员
            if i < len(selected_analysts) - 1:
                next_analyst = f"{selected_analysts[i+1].capitalize()} Analyst"
                workflow.add_edge(current_clear, next_analyst)
            else:
                workflow.add_edge(current_clear, "Bull Researcher")

        # Add remaining edges
        # 添加剩余的边
        workflow.add_conditional_edges(
            "Bull Researcher",
            self.conditional_logic.should_continue_debate,
            {
                "Bear Researcher": "Bear Researcher",
                "Research Manager": "Research Manager",
            },
        )
        workflow.add_conditional_edges(
            "Bear Researcher",
            self.conditional_logic.should_continue_debate,
            {
                "Bull Researcher": "Bull Researcher",
                "Research Manager": "Research Manager",
            },
        )
        workflow.add_edge("Research Manager", "Trader")
        workflow.add_edge("Trader", "Risky Analyst")
        workflow.add_conditional_edges(
            "Risky Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Safe Analyst": "Safe Analyst",
                "Risk Judge": "Risk Judge",
            },
        )
        workflow.add_conditional_edges(
            "Safe Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Neutral Analyst": "Neutral Analyst",
                "Risk Judge": "Risk Judge",
            },
        )
        workflow.add_conditional_edges(
            "Neutral Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Risky Analyst": "Risky Analyst",
                "Risk Judge": "Risk Judge",
            },
        )

        workflow.add_edge("Risk Judge", END)

        # Compile and return
        # 编译并返回
        return workflow.compile()
