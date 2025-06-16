# TradingAgents/default_config.py
# 该文件定义了交易代理框架的默认配置设置。

import os

# DEFAULT_CONFIG: 默认配置字典
DEFAULT_CONFIG = {
    # project_dir: 项目目录
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    # data_dir: 数据目录
    "data_dir": "/Users/yluo/Documents/Code/ScAI/FR1-data",
    # data_cache_dir: 数据缓存目录
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings: LLM设置
    "deep_think_llm": "o4-mini",
    "quick_think_llm": "gpt-4o-mini",
    # Debate and discussion settings: 辩论和讨论设置
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Tool settings: 工具设置
    "online_tools": True,
}
