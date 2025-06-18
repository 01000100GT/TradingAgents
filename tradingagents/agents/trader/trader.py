# 本文件定义了交易员代理的创建函数和交易逻辑，交易员根据分析师的投资计划和历史记忆做出最终交易决策。

import functools
import time
import json


# 创建交易员代理
def create_trader(llm, memory):
    # 交易员节点函数
    def trader_node(state, name):
        # 公司名称
        company_name = state["company_of_interest"]
        # 投资计划
        investment_plan = state["investment_plan"]
        # 市场研究报告
        market_research_report = state["market_report"]
        # 情绪报告
        sentiment_report = state["sentiment_report"]
        # 新闻报告
        news_report = state["news_report"]
        # 基本面报告
        fundamentals_report = state["fundamentals_report"]

        # 当前情况
        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        # 过去的记忆
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        # 上下文消息
        context = {
            "role": "user",
            "content": f"基于分析师团队的综合分析，这里是为{company_name}量身定制的投资计划。该计划融合了当前技术市场趋势、宏观经济指标和社交媒体情绪的见解。请以此计划为基础评估您的下一个交易决策。\n\n建议的投资计划：{investment_plan}\n\n利用这些见解做出明智的战略决策。",
        }

        # 消息列表
        messages = [
            {
                "role": "system",
                "content": f"""您是一位交易代理，分析市场数据以做出投资决策。基于您的分析，提供具体的买入、卖出或持有建议。以坚定的决策结束，并始终以'最终交易建议：**买入/持有/卖出**'结束您的回复以确认您的建议。不要忘记利用过去决策的经验教训来从错误中学习。以下是您在类似交易情况中的一些反思和学到的经验教训：{past_memory_str}""",
            },
            context,
        ]

        # 调用 LLM
        result = llm.invoke(messages)

        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
        }

    # 返回部分应用的交易员节点函数
    return functools.partial(trader_node, name="Trader")
