# TradingAgents/graph/trading_graph.py
# 该文件是交易代理框架的主类，负责协调整个流程。

import os
from pathlib import Path
import json
from datetime import date
from typing import Dict, Any, Tuple, List, Optional

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.prebuilt import ToolNode

from tradingagents.agents import *
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.agents.utils.memory import FinancialSituationMemory
from tradingagents.agents.utils.agent_states import (
    AgentState,
    InvestDebateState,
    RiskDebateState,
)
from tradingagents.agents.utils.agent_utils import create_chat_openai, create_openai_embeddings
from tradingagents.dataflows.interface import set_config

from .conditional_logic import ConditionalLogic
from .setup import GraphSetup
from .propagation import Propagator
from .reflection import Reflector
from .signal_processing import SignalProcessor


class TradingAgentsGraph:
    """
    交易代理图
    主要类，协调交易代理框架。
    Main class that orchestrates the trading agents framework.
    """

    def __init__(
        self,
        selected_analysts=["market", "social", "news", "fundamentals"],
        debug=False,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        初始化交易代理图和组件。
        Initialize the trading agents graph and components.

        Args:
            selected_analysts: 要包含的分析师类型列表
            debug: 是否在调试模式下运行
            config: 配置字典。如果为None，则使用默认配置
        """
        # debug: 调试模式
        self.debug = debug
        # config: 配置
        self.config = config or DEFAULT_CONFIG

        # Update the interface's config
        # 更新接口的配置
        set_config(self.config)

        # Create necessary directories
        # 创建必要的目录
        os.makedirs(
            os.path.join(self.config["project_dir"], "dataflows/data_cache"),
            exist_ok=True,
        )

        # Initialize LLMs using config
        # 使用配置初始化LLM
        # deep_thinking_llm: 深度思考LLM
        self.deep_thinking_llm = create_chat_openai(
            self.config, 
            model_name=self.config.get("deep_think_llm"),
            temperature=0.7
        )
        # quick_thinking_llm: 快速思考LLM
        self.quick_thinking_llm = create_chat_openai(
            self.config,
            model_name=self.config.get("quick_think_llm"), 
            temperature=0.1
        )
        
        # Initialize embedding model
        # 初始化嵌入模型
        self.embeddings = create_openai_embeddings(self.config)
        # toolkit: 工具包
        self.toolkit = Toolkit(config=self.config)

        # Initialize memories
        # 初始化记忆
        # bull_memory: 看涨记忆
        self.bull_memory = FinancialSituationMemory("bull_memory")
        # bear_memory: 看跌记忆
        self.bear_memory = FinancialSituationMemory("bear_memory")
        # trader_memory: 交易员记忆
        self.trader_memory = FinancialSituationMemory("trader_memory")
        # invest_judge_memory: 投资判断记忆
        self.invest_judge_memory = FinancialSituationMemory("invest_judge_memory")
        # risk_manager_memory: 风险经理记忆
        self.risk_manager_memory = FinancialSituationMemory("risk_manager_memory")

        # Create tool nodes
        # 创建工具节点
        self.tool_nodes = self._create_tool_nodes()

        # Initialize components
        # 初始化组件
        # conditional_logic: 条件逻辑
        self.conditional_logic = ConditionalLogic()
        # graph_setup: 图配置
        self.graph_setup = GraphSetup(
            self.config,  # 传入配置而不是LLM实例
            self.config,  # 传入配置而不是LLM实例
            self.toolkit,
            self.tool_nodes,
            self.bull_memory,
            self.bear_memory,
            self.trader_memory,
            self.invest_judge_memory,
            self.risk_manager_memory,
            self.conditional_logic,
            self.config,
        )

        # propagator: 传播器
        self.propagator = Propagator()
        # reflector: 反射器
        self.reflector = Reflector(self.config)  # 传入配置
        # signal_processor: 信号处理器
        self.signal_processor = SignalProcessor(self.config)  # 传入配置

        # State tracking
        # 状态跟踪
        # curr_state: 当前状态
        self.curr_state = None
        # ticker: 股票代码
        self.ticker = None
        # log_states_dict: 日志状态字典
        self.log_states_dict = {}  # date to full state dict

        # Set up the graph
        # 设置图
        self.graph = self.graph_setup.setup_graph(selected_analysts)

    def _create_tool_nodes(self) -> Dict[str, ToolNode]:
        """
        为不同数据源创建工具节点。
        Create tool nodes for different data sources.
        """
        return {
            "market": ToolNode(
                [
                    # online tools
                    # 在线工具
                    self.toolkit.get_YFin_data_online,
                    self.toolkit.get_stockstats_indicators_report_online,
                    # offline tools
                    # 离线工具
                    self.toolkit.get_YFin_data,
                    self.toolkit.get_stockstats_indicators_report,
                ]
            ),
            "social": ToolNode(
                [
                    # online tools
                    # 在线工具
                    self.toolkit.get_stock_news_openai,
                    # offline tools
                    # 离线工具
                    self.toolkit.get_reddit_stock_info,
                ]
            ),
            "news": ToolNode(
                [
                    # online tools
                    # 在线工具
                    self.toolkit.get_global_news_openai,
                    self.toolkit.get_google_news,
                    # offline tools
                    # 离线工具
                    self.toolkit.get_finnhub_news,
                    self.toolkit.get_reddit_news,
                ]
            ),
            "fundamentals": ToolNode(
                [
                    # online tools
                    # 在线工具
                    self.toolkit.get_fundamentals_openai,
                    # offline tools
                    # 离线工具
                    self.toolkit.get_finnhub_company_insider_sentiment,
                    self.toolkit.get_finnhub_company_insider_transactions,
                    self.toolkit.get_simfin_balance_sheet,
                    self.toolkit.get_simfin_cashflow,
                    self.toolkit.get_simfin_income_stmt,
                ]
            ),
        }

    def propagate(self, company_name, trade_date):
        """
        在特定日期为公司运行交易代理图。
        Run the trading agents graph for a company on a specific date.
        """
        # ticker: 股票代码
        self.ticker = company_name

        # Initialize state
        # 初始化状态
        # init_agent_state: 初始代理状态
        init_agent_state = self.propagator.create_initial_state(
            company_name, trade_date
        )
        # args: 参数
        args = self.propagator.get_graph_args()

        if self.debug:
            # Debug mode with tracing
            # 调试模式带追踪
            # trace: 追踪
            trace = []
            for chunk in self.graph.stream(init_agent_state, **args):
                if len(chunk["messages"]) == 0:
                    pass
                else:
                    chunk["messages"][-1].pretty_print()
                    trace.append(chunk)

            # final_state: 最终状态
            final_state = trace[-1]
        else:
            # Standard mode without tracing
            # 标准模式不带追踪
            final_state = self.graph.invoke(init_agent_state, **args)

        # Store current state for reflection
        # 存储当前状态以供反射
        self.curr_state = final_state

        # Log state
        # 记录状态
        self._log_state(trade_date, final_state)

        # Return decision and processed signal
        # 返回决策和处理后的信号
        return final_state, self.process_signal(final_state["final_trade_decision"])

    def _log_state(self, trade_date, final_state):
        """
        将最终状态记录到JSON文件。
        Log the final state to a JSON file.
        """
        self.log_states_dict[str(trade_date)] = {
            "company_of_interest": final_state["company_of_interest"],
            "trade_date": final_state["trade_date"],
            "market_report": final_state["market_report"],
            "sentiment_report": final_state["sentiment_report"],
            "news_report": final_state["news_report"],
            "fundamentals_report": final_state["fundamentals_report"],
            "investment_debate_state": {
                "bull_history": final_state["investment_debate_state"]["bull_history"],
                "bear_history": final_state["investment_debate_state"]["bear_history"],
                "history": final_state["investment_debate_state"]["history"],
                "current_response": final_state["investment_debate_state"][
                    "current_response"
                ],
                "judge_decision": final_state["investment_debate_state"][
                    "judge_decision"
                ],
            },
            "trader_investment_decision": final_state["trader_investment_plan"],
            "risk_debate_state": {
                "risky_history": final_state["risk_debate_state"]["risky_history"],
                "safe_history": final_state["risk_debate_state"]["safe_history"],
                "neutral_history": final_state["risk_debate_state"]["neutral_history"],
                "history": final_state["risk_debate_state"]["history"],
                "judge_decision": final_state["risk_debate_state"]["judge_decision"],
            },
            "investment_plan": final_state["investment_plan"],
            "final_trade_decision": final_state["final_trade_decision"],
        }

        # Save to file
        # 保存到文件
        # directory: 目录
        directory = Path(f"eval_results/{self.ticker}/TradingAgentsStrategy_logs/")
        directory.mkdir(parents=True, exist_ok=True)

        with open(
            f"eval_results/{self.ticker}/TradingAgentsStrategy_logs/full_states_log.json",
            "w",
        ) as f:
            json.dump(self.log_states_dict, f, indent=4)

    def reflect_and_remember(self, returns_losses):
        """
        根据回报反思决策并更新记忆。
        Reflect on decisions and update memory based on returns.
        """
        self.reflector.reflect_bull_researcher(
            self.curr_state, returns_losses, self.bull_memory
        )
        self.reflector.reflect_bear_researcher(
            self.curr_state, returns_losses, self.bear_memory
        )
        self.reflector.reflect_trader(
            self.curr_state, returns_losses, self.trader_memory
        )
        self.reflector.reflect_invest_judge(
            self.curr_state, returns_losses, self.invest_judge_memory
        )
        self.reflector.reflect_risk_manager(
            self.curr_state, returns_losses, self.risk_manager_memory
        )

    def process_signal(self, full_signal):
        """
        处理信号以提取核心决策。
        Process a signal to extract the core decision.
        """
        return self.signal_processor.process_signal(full_signal)
