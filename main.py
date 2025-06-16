# main.py
# 该文件是交易代理框架的入口点，演示了如何初始化和使用TradingAgentsGraph。

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Create a custom config
# 创建自定义配置
# config: 配置
config = DEFAULT_CONFIG.copy()
# deep_think_llm: 深度思考LLM模型
config["deep_think_llm"] = "gpt-4.1-nano"  # Use a different model
# quick_think_llm: 快速思考LLM模型
config["quick_think_llm"] = "gpt-4.1-nano"  # Use a different model
# max_debate_rounds: 最大辩论轮数
config["max_debate_rounds"] = 1  # Increase debate rounds
# online_tools: 是否使用在线工具
config["online_tools"] = True  # Increase debate rounds

# Initialize with custom config
# 使用自定义配置初始化
# ta: TradingAgentsGraph实例
ta = TradingAgentsGraph(debug=True, config=config)

# forward propagate
# 前向传播
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)

# Memorize mistakes and reflect
# 记忆错误并反思
# ta.reflect_and_remember(1000) # parameter is the position returns
