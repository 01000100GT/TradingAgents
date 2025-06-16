# config.py
#
# 该文件用于管理交易代理的配置设置。
# 允许从默认配置初始化，并支持通过自定义值进行覆盖。
import tradingagents.default_config as default_config
from typing import Dict, Optional

# 使用默认配置，但允许其被覆盖
_config: Optional[Dict] = None
DATA_DIR: Optional[str] = None


def initialize_config():
    """
    初始化配置。
    使用默认值初始化全局配置字典 `_config` 和数据目录 `DATA_DIR`。
    如果 `_config` 已经初始化，则不执行任何操作。
    """
    global _config, DATA_DIR
    if _config is None:
        _config = default_config.DEFAULT_CONFIG.copy()
        DATA_DIR = _config["data_dir"]


def set_config(config: Dict):
    """
    更新配置。
    使用提供的字典 `config` 更新全局配置字典 `_config`。
    如果 `_config` 尚未初始化，则先用默认值初始化它。
    同时更新 `DATA_DIR`。
    Args:
        config (Dict): 包含要更新的配置值的字典。
    """
    global _config, DATA_DIR
    if _config is None:
        _config = default_config.DEFAULT_CONFIG.copy()
    _config.update(config)
    DATA_DIR = _config["data_dir"]


def get_config() -> Dict:
    """
    获取当前配置。
    返回当前全局配置字典 `_config` 的一个副本。
    如果 `_config` 尚未初始化，则先用默认值初始化它。
    Returns:
        Dict: 当前配置的副本。
    """
    if _config is None:
        initialize_config()
    return _config.copy()


# 使用默认配置进行初始化
initialize_config()
