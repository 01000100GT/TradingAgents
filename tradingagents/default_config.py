# TradingAgents/default_config.py
# 该文件定义了交易代理框架的默认配置设置。

import os
import yaml
from pathlib import Path

def load_model_config():
    """从conf.yaml文件加载模型配置"""
    config_path = Path(__file__).parent.parent / "conf.yaml"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            yaml_config = yaml.safe_load(f)
            return yaml_config.get('BASIC_MODEL', {})
    return {}

# 加载模型配置
MODEL_CONFIG = load_model_config()

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
    # LLM settings: LLM设置 - 从conf.yaml读取
    "model_config": MODEL_CONFIG,
    "deep_think_llm": MODEL_CONFIG.get("model", "o4-mini"),
    "quick_think_llm": MODEL_CONFIG.get("model", "gpt-4o-mini"),
    "base_url": MODEL_CONFIG.get("base_url"),
    "api_key": MODEL_CONFIG.get("api_key"),
    
    # Embedding model settings: 嵌入模型设置
    "embedding_model": MODEL_CONFIG.get("embedding_model", "text-embedding-3-small"),
    "embedding_base_url": MODEL_CONFIG.get("embedding_base_url", MODEL_CONFIG.get("base_url")),
    "embedding_api_key": MODEL_CONFIG.get("embedding_api_key", MODEL_CONFIG.get("api_key")),
    
    # Debate and discussion settings: 辩论和讨论设置
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Tool settings: 工具设置
    "online_tools": True,
}
