# models.py
# 这个文件定义了CLI应用程序中使用的数据模型和枚举。
# 它包含了分析师类型的枚举，以及未来可能用于其他数据结构的基类。

from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel


# 分析师类型枚举
class AnalystType(str, Enum):
    # 市场分析师
    MARKET = "market"
    # 社交媒体分析师
    SOCIAL = "social"
    # 新闻分析师
    NEWS = "news"
    # 基本面分析师
    FUNDAMENTALS = "fundamentals"
