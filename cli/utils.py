# utils.py
# 这个文件包含了CLI应用程序的实用函数，主要用于处理用户输入。
# 它定义了获取股票代码、分析日期、选择分析师以及研究深度和思考代理的逻辑。

import questionary
from typing import List, Optional, Tuple, Dict
from rich.console import Console

from cli.models import AnalystType

# 控制台对象，用于Rich库的输出
console = Console()

# 分析师顺序列表，包含显示名称和对应的枚举值
ANALYST_ORDER = [
    ("Market Analyst", AnalystType.MARKET),
    ("Social Media Analyst", AnalystType.SOCIAL),
    ("News Analyst", AnalystType.NEWS),
    ("Fundamentals Analyst", AnalystType.FUNDAMENTALS),
]


# 获取股票代码
def get_ticker() -> str:
    """Prompt the user to enter a ticker symbol."""
    ticker = questionary.text(
        "Enter the ticker symbol to analyze:",
        validate=lambda x: len(x.strip()) > 0 or "Please enter a valid ticker symbol.",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not ticker:
        # 控制台打印错误信息
        console.print("\n[red]No ticker symbol provided. Exiting...[/red]")
        exit(1)

    return ticker.strip().upper()


# 获取分析日期
def get_analysis_date() -> str:
    """Prompt the user to enter a date in YYYY-MM-DD format."""
    import re
    from datetime import datetime

    # 验证日期格式
    def validate_date(date_str: str) -> bool:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    date = questionary.text(
        "Enter the analysis date (YYYY-MM-DD):",
        validate=lambda x: validate_date(x.strip())
        or "Please enter a valid date in YYYY-MM-DD format.",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not date:
        # 控制台打印错误信息
        console.print("\n[red]No date provided. Exiting...[/red]")
        exit(1)

    return date.strip()


# 选择分析师
def select_analysts() -> List[AnalystType]:
    """Select analysts using an interactive checkbox."""
    choices = questionary.checkbox(
        "Select Your [Analysts Team]:",
        choices=[
            questionary.Choice(display, value=value) for display, value in ANALYST_ORDER
        ],
        instruction="\n- Press Space to select/unselect analysts\n- Press 'a' to select/unselect all\n- Press Enter when done",
        validate=lambda x: len(x) > 0 or "You must select at least one analyst.",
        style=questionary.Style(
            [
                ("checkbox-selected", "fg:green"),
                ("selected", "fg:green noinherit"),
                ("highlighted", "noinherit"),
                ("pointer", "noinherit"),
            ]
        ),
    ).ask()

    if not choices:
        # 控制台打印错误信息
        console.print("\n[red]No analysts selected. Exiting...[/red]")
        exit(1)

    return choices


# 选择研究深度
def select_research_depth() -> int:
    """Select research depth using an interactive selection."""

    # Define research depth options with their corresponding values
    # 定义研究深度选项及其对应值
    DEPTH_OPTIONS = [
        ("Shallow - Quick research, few debate and strategy discussion rounds", 1),
        ("Medium - Middle ground, moderate debate rounds and strategy discussion", 3),
        ("Deep - Comprehensive research, in depth debate and strategy discussion", 5),
    ]

    choice = questionary.select(
        "Select Your [Research Depth]:",
        choices=[
            questionary.Choice(display, value=value) for display, value in DEPTH_OPTIONS
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:yellow noinherit"),
                ("highlighted", "fg:yellow noinherit"),
                ("pointer", "fg:yellow noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        # 控制台打印错误信息
        console.print("\n[red]No research depth selected. Exiting...[/red]")
        exit(1)

    return choice


# 选择浅层思考LLM引擎
def select_shallow_thinking_agent() -> str:
    """Select shallow thinking llm engine using an interactive selection."""

    # Define shallow thinking llm engine options with their corresponding model names
    # 定义浅层思考LLM引擎选项及其对应的模型名称
    SHALLOW_AGENT_OPTIONS = [
        ("GPT-4o-mini - Fast and efficient for quick tasks", "gpt-4o-mini"),
        ("GPT-4.1-nano - Ultra-lightweight model for basic operations", "gpt-4.1-nano"),
        ("GPT-4.1-mini - Compact model with good performance", "gpt-4.1-mini"),
        ("GPT-4o - Standard model with solid capabilities", "gpt-4o"),
        ("Qwen/Qwen3-8B - Efficient Chinese-optimized model", "Qwen/Qwen3-8B"),
    ]

    choice = questionary.select(
        "Select Your [Quick-Thinking LLM Engine]:",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in SHALLOW_AGENT_OPTIONS
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        # 控制台打印错误信息
        console.print(
            "\n[red]No shallow thinking llm engine selected. Exiting...[/red]"
        )
        exit(1)

    return choice


# 选择深层思考LLM引擎
def select_deep_thinking_agent() -> str:
    """Select deep thinking llm engine using an interactive selection."""

    # Define deep thinking llm engine options with their corresponding model names
    # 定义深层思考LLM引擎选项及其对应的模型名称
    DEEP_AGENT_OPTIONS = [
        ("GPT-4.1-nano - Ultra-lightweight model for basic operations", "gpt-4.1-nano"),
        ("GPT-4.1-mini - Compact model with good performance", "gpt-4.1-mini"),
        ("GPT-4o - Standard model with solid capabilities", "gpt-4o"),
        ("o4-mini - Specialized reasoning model (compact)", "o4-mini"),
        ("o3-mini - Advanced reasoning model (lightweight)", "o3-mini"),
        ("o3 - Full advanced reasoning model", "o3"),
        ("o1 - Premier reasoning and problem-solving model", "o1"),
        ("Qwen/Qwen3-8B - Efficient Chinese-optimized model", "Qwen/Qwen3-8B"),
    ]

    choice = questionary.select(
        "Select Your [Deep-Thinking LLM Engine]:",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in DEEP_AGENT_OPTIONS
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        # 控制台打印错误信息
        console.print("\n[red]No deep thinking llm engine selected. Exiting...[/red]")
        exit(1)

    return choice
