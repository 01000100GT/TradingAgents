"""
Setup script for the TradingAgents package.
"""

from setuptools import setup, find_packages

setup(
    name="tradingagents",
    version="0.1.0",
    description="Multi-Agents LLM Financial Trading Framework",
    author="TradingAgents Team",
    author_email="yijia.xiao@cs.ucla.edu",
    url="https://github.com/TauricResearch",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.1.0",  # 用于构建基于大型语言模型的应用程序的框架
        "langchain-openai>=0.0.2",  # LangChain 的 OpenAI 集成
        "langchain-experimental>=0.0.40",  # LangChain 的实验性功能
        "langgraph>=0.0.20",  # 用于构建有状态、多角色 LLM 应用程序的库，LangChain 的一部分
        "numpy>=1.24.0",  # 科学计算库
        "pandas>=2.0.0",  # 数据操作和分析库
        "praw>=7.7.0",  # Python Reddit API 包装器
        "stockstats>=0.5.4",  # 股票统计数据计算库
        "yfinance>=0.2.31",  # Yahoo Finance 数据下载器
        "typer>=0.9.0",  # 用于构建命令行应用程序的库
        "rich>=13.0.0",  # 用于在终端中实现富文本和美观格式的库
        "questionary>=2.0.1",  # 用于交互式命令行提示的库
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "tradingagents=cli.main:app",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Trading Industry",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
) 