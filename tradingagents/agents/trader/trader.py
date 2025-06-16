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
            "content": f"Based on a comprehensive analysis by a team of analysts, here is an investment plan tailored for {company_name}. This plan incorporates insights from current technical market trends, macroeconomic indicators, and social media sentiment. Use this plan as a foundation for evaluating your next trading decision.\n\nProposed Investment Plan: {investment_plan}\n\nLeverage these insights to make an informed and strategic decision.",
        }

        # 消息列表
        messages = [
            {
                "role": "system",
                "content": f"""You are a trading agent analyzing market data to make investment decisions. Based on your analysis, provide a specific recommendation to buy, sell, or hold. End with a firm decision and always conclude your response with 'FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**' to confirm your recommendation. Do not forget to utilize lessons from past decisions to learn from your mistakes. Here is some reflections from similar situatiosn you traded in and the lessons learned: {past_memory_str}""",
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
