# main.py
# 这个文件是TradingAgents CLI应用程序的主入口点。
# 它负责设置Rich库的显示布局，处理用户输入，
# 并协调TradingAgentsGraph来执行金融市场分析。

from typing import Optional
import datetime
import typer
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from rich.columns import Columns
from rich.markdown import Markdown
from rich.layout import Layout
from rich.text import Text
from rich.live import Live
from rich.table import Table
from collections import deque
import time
from rich.tree import Tree
from rich import box
from rich.align import Align
from rich.rule import Rule

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from cli.models import AnalystType
from cli.utils import *

# 控制台对象，用于Rich库的输出
console = Console()

# Typer应用程序实例
app = typer.Typer(
    name="TradingAgents",
    help="TradingAgents CLI：多代理LLM金融交易框架",
    add_completion=True,  # 启用shell补全
)


# 消息缓冲区类，用于存储最近的消息、工具调用和代理状态
class MessageBuffer:
    def __init__(self, max_length=100):
        # 存储消息的双端队列
        self.messages = deque(maxlen=max_length)
        # 存储工具调用的双端队列
        self.tool_calls = deque(maxlen=max_length)
        # 当前报告
        self.current_report = None
        # 最终报告
        self.final_report = None  # 存储完整的最终报告
        # 代理状态字典
        self.agent_status = {
            # 分析师团队
            "Market Analyst": "pending",
            "Social Analyst": "pending",
            "News Analyst": "pending",
            "Fundamentals Analyst": "pending",
            # 研究团队
            "Bull Researcher": "pending",
            "Bear Researcher": "pending",
            "Research Manager": "pending",
            # 交易团队
            "Trader": "pending",
            # 风险管理团队
            "Risky Analyst": "pending",
            "Neutral Analyst": "pending",
            "Safe Analyst": "pending",
            # 投资组合管理团队
            "Portfolio Manager": "pending",
        }
        # 当前代理
        self.current_agent = None
        # 报告部分字典
        self.report_sections = {
            "market_report": None,
            "sentiment_report": None,
            "news_report": None,
            "fundamentals_report": None,
            "investment_plan": None,
            "trader_investment_plan": None,
            "final_trade_decision": None,
        }

    # 添加消息到缓冲区
    def add_message(self, message_type, content):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.messages.append((timestamp, message_type, content))

    # 添加工具调用到缓冲区
    def add_tool_call(self, tool_name, args):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.tool_calls.append((timestamp, tool_name, args))

    # 更新代理状态
    def update_agent_status(self, agent, status):
        if agent in self.agent_status:
            self.agent_status[agent] = status
            self.current_agent = agent

    # 更新报告部分
    def update_report_section(self, section_name, content):
        if section_name in self.report_sections:
            self.report_sections[section_name] = content
            self._update_current_report()

    # 更新当前报告
    def _update_current_report(self):
        # 对于面板显示，仅展示最近更新的部分
        latest_section = None
        latest_content = None

        # 找到最近更新的部分
        for section, content in self.report_sections.items():
            if content is not None:
                latest_section = section
                latest_content = content

        if latest_section and latest_content:
            # 格式化当前部分以供显示
            section_titles = {
                "market_report": "市场分析",
                "sentiment_report": "社交情绪",
                "news_report": "新闻分析",
                "fundamentals_report": "基本面分析",
                "investment_plan": "研究团队决策",
                "trader_investment_plan": "交易团队计划",
                "final_trade_decision": "投资组合管理决策",
            }
            self.current_report = (
                f"### {section_titles[latest_section]}\n{latest_content}"
            )

        # 更新最终完整报告
        self._update_final_report()

    # 更新最终报告
    def _update_final_report(self):
        report_parts = []

        # 分析师团队报告
        if any(
            self.report_sections[section]
            for section in [
                "market_report",
                "sentiment_report",
                "news_report",
                "fundamentals_report",
            ]
        ):
            report_parts.append("## 分析师团队报告")
            if self.report_sections["market_report"]:
                report_parts.append(
                    f"### 市场分析\n{self.report_sections['market_report']}"
                )
            if self.report_sections["sentiment_report"]:
                report_parts.append(
                    f"### 社交情绪\n{self.report_sections['sentiment_report']}"
                )
            if self.report_sections["news_report"]:
                report_parts.append(
                    f"### 新闻分析\n{self.report_sections['news_report']}"
                )
            if self.report_sections["fundamentals_report"]:
                report_parts.append(
                    f"### 基本面分析\n{self.report_sections['fundamentals_report']}"
                )

        # 研究团队报告
        if self.report_sections["investment_plan"]:
            report_parts.append("## 研究团队决策")
            report_parts.append(f"{self.report_sections['investment_plan']}")

        # 交易团队报告
        if self.report_sections["trader_investment_plan"]:
            report_parts.append("## 交易团队计划")
            report_parts.append(f"{self.report_sections['trader_investment_plan']}")

        # 投资组合管理决策
        if self.report_sections["final_trade_decision"]:
            report_parts.append("## 投资组合管理决策")
            report_parts.append(f"{self.report_sections['final_trade_decision']}")

        self.final_report = "\n\n".join(report_parts) if report_parts else None


# 消息缓冲区实例
message_buffer = MessageBuffer()


# 创建布局
def create_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3),
    )
    layout["main"].split_column(
        Layout(name="upper", ratio=3), Layout(name="analysis", ratio=5)
    )
    layout["upper"].split_row(
        Layout(name="progress", ratio=2), Layout(name="messages", ratio=3)
    )
    return layout


# 更新显示
def update_display(layout, spinner_text=None):
    # 带有欢迎消息的头部
    layout["header"].update(
        Panel(
            "[bold green]欢迎使用TradingAgents CLI[/bold green]\n"
            "[dim]© [Tauric Research](https://github.com/TauricResearch)[/dim]",
            title="欢迎使用TradingAgents",
            border_style="green",
            padding=(1, 2),
            expand=True,
        )
    )

    # 进度面板显示代理状态
    progress_table = Table(
        show_header=True,
        header_style="bold magenta",
        show_footer=False,
        box=box.SIMPLE_HEAD,  # 使用简单的头部带横线
        title=None,  # 移除多余的进度标题
        padding=(0, 2),  # 添加水平填充
        expand=True,  # 使表格扩展以填充可用空间
    )
    progress_table.add_column("团队", style="cyan", justify="center", width=20)
    progress_table.add_column("代理", style="green", justify="center", width=20)
    progress_table.add_column("状态", style="yellow", justify="center", width=20)

    # 按团队分组代理
    teams = {
        "分析师团队": [
            "Market Analyst",
            "Social Analyst",
            "News Analyst",
            "Fundamentals Analyst",
        ],
        "研究团队": ["Bull Researcher", "Bear Researcher", "Research Manager"],
        "交易团队": ["Trader"],
        "风险管理": ["Risky Analyst", "Neutral Analyst", "Safe Analyst"],
        "投资组合管理": ["Portfolio Manager"],
    }

    for team, agents in teams.items():
        # 添加第一个带有团队名称的代理
        first_agent = agents[0]
        status = message_buffer.agent_status[first_agent]
        if status == "in_progress":
            spinner = Spinner(
                "dots", text="[blue]进行中[/blue]", style="bold cyan"
            )
            status_cell = spinner
        else:
            status_color = {
                "pending": "yellow",
                "completed": "green",
                "error": "red",
            }.get(status, "white")
            status_cell = f"[{status_color}]{status}[/{status_color}]"
        progress_table.add_row(team, first_agent, status_cell)

        # 添加团队中的其余代理
        for agent in agents[1:]:
            status = message_buffer.agent_status[agent]
            if status == "in_progress":
                spinner = Spinner(
                    "dots", text="[blue]进行中[/blue]", style="bold cyan"
                )
                status_cell = spinner
            else:
                status_color = {
                    "pending": "yellow",
                    "completed": "green",
                    "error": "red",
                }.get(status, "white")
                status_cell = f"[{status_color}]{status}[/{status_color}]"
            progress_table.add_row("", agent, status_cell)

        # 在每个团队后添加横线
        progress_table.add_row("─" * 20, "─" * 20, "─" * 20, style="dim")

    layout["progress"].update(
        Panel(progress_table, title="进度", border_style="cyan", padding=(1, 2))
    )

    # 消息面板显示最近的消息和工具调用
    messages_table = Table(
        show_header=True,
        header_style="bold magenta",
        show_footer=False,
        expand=True,  # 使表格扩展以填充可用空间
        box=box.MINIMAL,  # 使用简约的框风格以获得更轻盈的外观
        show_lines=True,  # 保留水平线
        padding=(0, 1),  # 在列之间添加一些填充
    )
    messages_table.add_column("时间", style="cyan", width=8, justify="center")
    messages_table.add_column("类型", style="green", width=10, justify="center")
    messages_table.add_column(
        "内容", style="white", no_wrap=False, ratio=1
    )  # 使内容列扩展

    # 合并工具调用和消息
    all_messages = []

    # 添加工具调用
    for timestamp, tool_name, args in message_buffer.tool_calls:
        # 如果工具调用参数过长则截断
        if isinstance(args, str) and len(args) > 100:
            args = args[:97] + "..."
        all_messages.append((timestamp, "工具", f"{tool_name}: {args}"))

    # 添加常规消息
    for timestamp, msg_type, content in message_buffer.messages:
        # 如果消息内容过长则截断
        if isinstance(content, str) and len(content) > 200:
            content = content[:197] + "..."
        all_messages.append((timestamp, msg_type, content))

    # 按时间戳排序
    all_messages.sort(key=lambda x: x[0])

    # 根据可用空间计算我们可以显示的消息数量
    # 从一个合理的数字开始，并根据内容长度进行调整
    max_messages = 12  # 从8增加到12以更好地填充空间

    # 获取最后N条适合面板的消息
    recent_messages = all_messages[-max_messages:]

    # 将消息添加到表格
    for timestamp, msg_type, content in recent_messages:
        # 格式化内容以支持自动换行
        wrapped_content = Text(content, overflow="fold")
        messages_table.add_row(timestamp, msg_type, wrapped_content)

    if spinner_text:
        messages_table.add_row("", "加载", spinner_text)

    # 添加脚注以指示消息是否被截断
    if len(all_messages) > max_messages:
        messages_table.footer = (
            f"[dim]显示最后 {max_messages} 条，共 {len(all_messages)} 条消息[/dim]"
        )

    layout["messages"].update(
        Panel(
            messages_table,
            title="消息和工具",
            border_style="blue",
            padding=(1, 2),
        )
    )

    # 分析面板显示当前报告
    if message_buffer.current_report:
        layout["analysis"].update(
            Panel(
                Markdown(message_buffer.current_report),
                title="当前报告",
                border_style="green",
                padding=(1, 2),
            )
        )
    else:
        layout["analysis"].update(
            Panel(
                "[italic]等待分析报告...[/italic]",
                title="当前报告",
                border_style="green",
                padding=(1, 2),
            )
        )

    # 带有统计数据的脚部
    # 工具调用次数
    tool_calls_count = len(message_buffer.tool_calls)
    # LLM调用次数
    llm_calls_count = sum(
        1 for _, msg_type, _ in message_buffer.messages if msg_type == "Reasoning"
    )
    # 生成报告次数
    reports_count = sum(
        1 for content in message_buffer.report_sections.values() if content is not None
    )

    stats_table = Table(show_header=False, box=None, padding=(0, 2), expand=True)
    stats_table.add_column("统计", justify="center")
    stats_table.add_row(
        f"工具调用: {tool_calls_count} | LLM调用: {llm_calls_count} | 生成报告: {reports_count}"
    )

    layout["footer"].update(Panel(stats_table, border_style="grey50"))


# 获取用户选择
def get_user_selections():
    """获取分析显示开始前的所有用户选择。"""
    # 显示ASCII艺术欢迎消息
    with open("./cli/static/welcome.txt", "r") as f:
        welcome_ascii = f.read()

    # 创建欢迎框内容
    welcome_content = f"{welcome_ascii}\n"
    welcome_content += "[bold green]TradingAgents: 多代理LLM金融交易框架 - CLI[/bold green]\n\n"
    welcome_content += "[bold]工作流程步骤:[/bold]\n"
    welcome_content += "I. 分析师团队 → II. 研究团队 → III. 交易员 → IV. 风险管理 → V. 投资组合管理\n\n"
    welcome_content += (
        "[dim]由 [Tauric Research](https://github.com/TauricResearch) 构建[/dim]"
    )

    # 创建并居中欢迎框
    welcome_box = Panel(
        welcome_content,
        border_style="green",
        padding=(1, 2),
        title="欢迎使用TradingAgents",
        subtitle="多代理LLM金融交易框架",
    )
    console.print(Align.center(welcome_box))
    console.print()  # 在欢迎框后添加空行

    # 为每个步骤创建问卷框
    def create_question_box(title, prompt, default=None):
        box_content = f"[bold]{title}[/bold]\n"
        box_content += f"[dim]{prompt}[/dim]"
        if default:
            box_content += f"\n[dim]默认: {default}[/dim]"
        return Panel(box_content, border_style="blue", padding=(1, 2))

    # 步骤1：股票代码
    console.print(
        create_question_box(
            "步骤1：股票代码", "输入要分析的股票代码", "SPY"
        )
    )
    # 获取股票代码
    selected_ticker = get_ticker()

    # 步骤2：分析日期
    default_date = datetime.datetime.now().strftime("%Y-%m-%d")
    console.print(
        create_question_box(
            "步骤2：分析日期",
            "输入分析日期 (YYYY-MM-DD)",
            default_date,
        )
    )
    # 获取分析日期
    analysis_date = get_analysis_date()

    # 步骤3：选择分析师
    console.print(
        create_question_box(
            "步骤3：分析师团队", "为分析选择您的LLM分析师代理"
        )
    )
    # 选择分析师
    selected_analysts = select_analysts()
    console.print(
        f"[green]已选择的分析师:[/green] {', '.join(analyst.value for analyst in selected_analysts)}"
    )

    # 步骤4：研究深度
    console.print(
        create_question_box(
            "步骤4：研究深度", "选择您的研究深度级别"
        )
    )
    # 选择研究深度
    selected_research_depth = select_research_depth()

    # 步骤5：思考代理
    console.print(
        create_question_box(
            "步骤5：思考代理", "为分析选择您的思考代理"
        )
    )
    # 选择浅层思考代理
    selected_shallow_thinker = select_shallow_thinking_agent()
    # 选择深层思考代理
    selected_deep_thinker = select_deep_thinking_agent()

    return {
        "ticker": selected_ticker,
        "analysis_date": analysis_date,
        "analysts": selected_analysts,
        "research_depth": selected_research_depth,
        "shallow_thinker": selected_shallow_thinker,
        "deep_thinker": selected_deep_thinker,
    }


# 获取股票代码
def get_ticker():
    """从用户输入获取股票代码。"""
    return typer.prompt("", default="SPY")


# 获取分析日期
def get_analysis_date():
    """从用户输入获取分析日期。"""
    while True:
        date_str = typer.prompt(
            "", default=datetime.datetime.now().strftime("%Y-%m-%d")
        )
        try:
            # 验证日期格式并确保不是未来日期
            analysis_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            if analysis_date.date() > datetime.datetime.now().date():
                console.print("[red]错误：分析日期不能是未来日期[/red]")
                continue
            return date_str
        except ValueError:
            console.print(
                "[red]错误：无效的日期格式。请使用YYYY-MM-DD[/red]"
            )


# 显示完整报告
def display_complete_report(final_state):
    """显示完整的分析报告，带有基于团队的面板。"""
    console.print("\n[bold green]完整分析报告[/bold green]\n")

    # I. 分析师团队报告
    analyst_reports = []

    # 市场分析师报告
    if final_state.get("market_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["market_report"]),
                title="市场分析师",
                border_style="blue",
                padding=(1, 2),
            )
        )

    # 社交分析师报告
    if final_state.get("sentiment_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["sentiment_report"]),
                title="社交分析师",
                border_style="blue",
                padding=(1, 2),
            )
        )

    # 新闻分析师报告
    if final_state.get("news_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["news_report"]),
                title="新闻分析师",
                border_style="blue",
                padding=(1, 2),
            )
        )

    # 基本面分析师报告
    if final_state.get("fundamentals_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["fundamentals_report"]),
                title="基本面分析师",
                border_style="blue",
                padding=(1, 2),
            )
        )

    if analyst_reports:
        console.print(
            Panel(
                Columns(analyst_reports, equal=True, expand=True),
                title="I. 分析师团队报告",
                border_style="cyan",
                padding=(1, 2),
            )
        )

    # II. 研究团队报告
    if final_state.get("investment_debate_state"):
        research_reports = []
        debate_state = final_state["investment_debate_state"]

        # 看涨研究员分析
        if debate_state.get("bull_history"):
            research_reports.append(
                Panel(
                    Markdown(debate_state["bull_history"]),
                    title="看涨研究员",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # 看跌研究员分析
        if debate_state.get("bear_history"):
            research_reports.append(
                Panel(
                    Markdown(debate_state["bear_history"]),
                    title="看跌研究员",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # 研究经理决策
        if debate_state.get("judge_decision"):
            research_reports.append(
                Panel(
                    Markdown(debate_state["judge_decision"]),
                    title="研究经理",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        if research_reports:
            console.print(
                Panel(
                    Columns(research_reports, equal=True, expand=True),
                    title="II. 研究团队决策",
                    border_style="magenta",
                    padding=(1, 2),
                )
            )

    # III. 交易团队报告
    if final_state.get("trader_investment_plan"):
        console.print(
            Panel(
                Panel(
                    Markdown(final_state["trader_investment_plan"]),
                    title="交易员",
                    border_style="blue",
                    padding=(1, 2),
                ),
                title="III. 交易团队计划",
                border_style="yellow",
                padding=(1, 2),
            )
        )

    # IV. 风险管理团队报告
    if final_state.get("risk_debate_state"):
        risk_reports = []
        risk_state = final_state["risk_debate_state"]

        # 激进（风险）分析师分析
        if risk_state.get("risky_history"):
            risk_reports.append(
                Panel(
                    Markdown(risk_state["risky_history"]),
                    title="激进分析师",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # 保守（安全）分析师分析
        if risk_state.get("safe_history"):
            risk_reports.append(
                Panel(
                    Markdown(risk_state["safe_history"]),
                    title="保守分析师",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # 中立分析师分析
        if risk_state.get("neutral_history"):
            risk_reports.append(
                Panel(
                    Markdown(risk_state["neutral_history"]),
                    title="中立分析师",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        if risk_reports:
            console.print(
                Panel(
                    Columns(risk_reports, equal=True, expand=True),
                    title="IV. 风险管理团队决策",
                    border_style="red",
                    padding=(1, 2),
                )
            )

        # V. 投资组合经理决策
        if risk_state.get("judge_decision"):
            console.print(
                Panel(
                    Panel(
                        Markdown(risk_state["judge_decision"]),
                        title="投资组合经理",
                        border_style="blue",
                        padding=(1, 2),
                    ),
                    title="V. 投资组合经理决策",
                    border_style="green",
                    padding=(1, 2),
                )
            )


# 更新研究团队状态
def update_research_team_status(status):
    """更新所有研究团队成员和交易员的状态。"""
    research_team = ["Bull Researcher", "Bear Researcher", "Research Manager", "Trader"]
    for agent in research_team:
        message_buffer.update_agent_status(agent, status)


# 运行分析
def run_analysis():
    # 首先获取所有用户选择
    selections = get_user_selections()

    # 根据选择的研究深度创建配置
    config = DEFAULT_CONFIG.copy()
    config["max_debate_rounds"] = selections["research_depth"]
    config["max_risk_discuss_rounds"] = selections["research_depth"]
    config["quick_think_llm"] = selections["shallow_thinker"]
    config["deep_think_llm"] = selections["deep_thinker"]

    # 初始化图
    graph = TradingAgentsGraph(
        [analyst.value for analyst in selections["analysts"]], config=config, debug=True
    )

    # 现在开始显示布局
    layout = create_layout()

    with Live(layout, refresh_per_second=4) as live:
        # 初始显示
        update_display(layout)

        # 添加初始消息
        message_buffer.add_message("System", f"已选择的股票代码: {selections['ticker']}")
        message_buffer.add_message(
            "System", f"分析日期: {selections['analysis_date']}"
        )
        message_buffer.add_message(
            "System",
            f"已选择的分析师: {', '.join(analyst.value for analyst in selections['analysts'])}",
        )
        update_display(layout)

        # 重置代理状态
        for agent in message_buffer.agent_status:
            message_buffer.update_agent_status(agent, "pending")

        # 重置报告部分
        for section in message_buffer.report_sections:
            message_buffer.report_sections[section] = None
        message_buffer.current_report = None
        message_buffer.final_report = None

        # 更新第一个分析师的代理状态为进行中
        first_analyst = f"{selections['analysts'][0].value.capitalize()} Analyst"
        message_buffer.update_agent_status(first_analyst, "in_progress")
        update_display(layout)

        # 创建加载文本
        spinner_text = (
            f"正在分析 {selections['ticker']} 于 {selections['analysis_date']}..."
        )
        update_display(layout, spinner_text)

        # 初始化状态并获取图参数
        init_agent_state = graph.propagator.create_initial_state(
            selections["ticker"], selections["analysis_date"]
        )
        args = graph.propagator.get_graph_args()

        # 流式传输分析
        trace = []
        for chunk in graph.graph.stream(init_agent_state, **args):
            if len(chunk["messages"]) > 0:
                # 获取块中的最后一条消息
                last_message = chunk["messages"][-1]

                # 提取消息内容和类型
                if hasattr(last_message, "content"):
                    content = last_message.content
                    msg_type = "推理"
                else:
                    content = str(last_message)
                    msg_type = "系统"

                # 添加消息到缓冲区
                message_buffer.add_message(msg_type, content)

                # 如果是工具调用，添加到工具调用中
                if hasattr(last_message, "tool_calls"):
                    for tool_call in last_message.tool_calls:
                        # 处理字典和对象工具调用
                        if isinstance(tool_call, dict):
                            message_buffer.add_tool_call(
                                tool_call["name"], tool_call["args"]
                            )
                        else:
                            message_buffer.add_tool_call(tool_call.name, tool_call.args)

                # 根据块内容更新报告和代理状态
                # 分析师团队报告
                if "market_report" in chunk and chunk["market_report"]:
                    message_buffer.update_report_section(
                        "market_report", chunk["market_report"]
                    )
                    message_buffer.update_agent_status("Market Analyst", "completed")
                    # 将下一个分析师设置为进行中
                    if "social" in selections["analysts"]:
                        message_buffer.update_agent_status(
                            "Social Analyst", "in_progress"
                        )

                if "sentiment_report" in chunk and chunk["sentiment_report"]:
                    message_buffer.update_report_section(
                        "sentiment_report", chunk["sentiment_report"]
                    )
                    message_buffer.update_agent_status("Social Analyst", "completed")
                    # 将下一个分析师设置为进行中
                    if "news" in selections["analysts"]:
                        message_buffer.update_agent_status(
                            "News Analyst", "in_progress"
                        )

                if "news_report" in chunk and chunk["news_report"]:
                    message_buffer.update_report_section(
                        "news_report", chunk["news_report"]
                    )
                    message_buffer.update_agent_status("News Analyst", "completed")
                    # 将下一个分析师设置为进行中
                    if "fundamentals" in selections["analysts"]:
                        message_buffer.update_agent_status(
                            "Fundamentals Analyst", "in_progress"
                        )

                if "fundamentals_report" in chunk and chunk["fundamentals_report"]:
                    message_buffer.update_report_section(
                        "fundamentals_report", chunk["fundamentals_report"]
                    )
                    message_buffer.update_agent_status(
                        "Fundamentals Analyst", "completed"
                    )
                    # 将所有研究团队成员设置为进行中
                    update_research_team_status("in_progress")

                # 研究团队 - 处理投资辩论状态
                if (
                    "investment_debate_state" in chunk
                    and chunk["investment_debate_state"]
                ):
                    debate_state = chunk["investment_debate_state"]

                    # 更新看涨研究员状态和报告
                    if "bull_history" in debate_state and debate_state["bull_history"]:
                        # 保持所有研究团队成员进行中
                        update_research_team_status("in_progress")
                        # 提取最新的看涨响应
                        bull_responses = debate_state["bull_history"].split("\n")
                        latest_bull = bull_responses[-1] if bull_responses else ""
                        if latest_bull:
                            message_buffer.add_message("推理", latest_bull)
                            # 用看涨研究员的最新分析更新研究报告
                            message_buffer.update_report_section(
                                "investment_plan",
                                f"### 看涨研究员分析\n{latest_bull}",
                            )

                    # 更新看跌研究员状态和报告
                    if "bear_history" in debate_state and debate_state["bear_history"]:
                        # 保持所有研究团队成员进行中
                        update_research_team_status("in_progress")
                        # 提取最新的看跌响应
                        bear_responses = debate_state["bear_history"].split("\n")
                        latest_bear = bear_responses[-1] if bear_responses else ""
                        if latest_bear:
                            message_buffer.add_message("推理", latest_bear)
                            # 用看跌研究员的最新分析更新研究报告
                            message_buffer.update_report_section(
                                "investment_plan",
                                f"{message_buffer.report_sections['investment_plan']}\n\n### 看跌研究员分析\n{latest_bear}",
                            )

                    # 更新研究经理状态和最终决定
                    if (
                        "judge_decision" in debate_state
                        and debate_state["judge_decision"]
                    ):
                        # 保持所有研究团队成员进行中直到最终决定
                        update_research_team_status("in_progress")
                        message_buffer.add_message(
                            "推理",
                            f"研究经理: {debate_state['judge_decision']}",
                        )
                        # 用最终决定更新研究报告
                        message_buffer.update_report_section(
                            "investment_plan",
                            f"{message_buffer.report_sections['investment_plan']}\n\n### 研究经理决策\n{debate_state['judge_decision']}",
                        )
                        # 将所有研究团队成员标记为已完成
                        update_research_team_status("completed")
                        # 将第一个风险分析师设置为进行中
                        message_buffer.update_agent_status(
                            "Risky Analyst", "in_progress"
                        )

                # 交易团队
                if (
                    "trader_investment_plan" in chunk
                    and chunk["trader_investment_plan"]
                ):
                    message_buffer.update_report_section(
                        "trader_investment_plan", chunk["trader_investment_plan"]
                    )
                    # 将第一个风险分析师设置为进行中
                    message_buffer.update_agent_status("Risky Analyst", "in_progress")

                # 风险管理团队 - 处理风险辩论状态
                if "risk_debate_state" in chunk and chunk["risk_debate_state"]:
                    risk_state = chunk["risk_debate_state"]

                    # 更新风险分析师状态和报告
                    if (
                        "current_risky_response" in risk_state
                        and risk_state["current_risky_response"]
                    ):
                        message_buffer.update_agent_status(
                            "Risky Analyst", "in_progress"
                        )
                        message_buffer.add_message(
                            "推理",
                            f"风险分析师: {risk_state['current_risky_response']}",
                        )
                        # 仅用风险分析师的最新分析更新风险报告
                        message_buffer.update_report_section(
                            "final_trade_decision",
                            f"### 风险分析师分析\n{risk_state['current_risky_response']}",
                        )

                    # 更新安全分析师状态和报告
                    if (
                        "current_safe_response" in risk_state
                        and risk_state["current_safe_response"]
                    ):
                        message_buffer.update_agent_status(
                            "Safe Analyst", "in_progress"
                        )
                        message_buffer.add_message(
                            "推理",
                            f"安全分析师: {risk_state['current_safe_response']}",
                        )
                        # 仅用安全分析师的最新分析更新风险报告
                        message_buffer.update_report_section(
                            "final_trade_decision",
                            f"### 安全分析师分析\n{risk_state['current_safe_response']}",
                        )

                    # 更新中立分析师状态和报告
                    if (
                        "current_neutral_response" in risk_state
                        and risk_state["current_neutral_response"]
                    ):
                        message_buffer.update_agent_status(
                            "Neutral Analyst", "in_progress"
                        )
                        message_buffer.add_message(
                            "推理",
                            f"中立分析师: {risk_state['current_neutral_response']}",
                        )
                        # 仅用中立分析师的最新分析更新风险报告
                        message_buffer.update_report_section(
                            "final_trade_decision",
                            f"### 中立分析师分析\n{risk_state['current_neutral_response']}",
                        )

                    # 更新投资组合经理状态和最终决定
                    if "judge_decision" in risk_state and risk_state["judge_decision"]:
                        message_buffer.update_agent_status(
                            "Portfolio Manager", "in_progress"
                        )
                        message_buffer.add_message(
                            "推理",
                            f"投资组合经理: {risk_state['judge_decision']}",
                        )
                        # 仅用最终决定更新风险报告
                        message_buffer.update_report_section(
                            "final_trade_decision",
                            f"### 投资组合经理决策\n{risk_state['judge_decision']}",
                        )
                        # 将风险分析师标记为已完成
                        message_buffer.update_agent_status("Risky Analyst", "completed")
                        message_buffer.update_agent_status("Safe Analyst", "completed")
                        message_buffer.update_agent_status(
                            "Neutral Analyst", "completed"
                        )
                        message_buffer.update_agent_status(
                            "Portfolio Manager", "completed"
                        )

                # 更新显示
                update_display(layout)

            trace.append(chunk)

        # 获取最终状态和决定
        final_state = trace[-1]
        decision = graph.process_signal(final_state["final_trade_decision"])

        # 将所有代理状态更新为已完成
        for agent in message_buffer.agent_status:
            message_buffer.update_agent_status(agent, "completed")

        message_buffer.add_message(
            "分析", f"完成对 {selections['analysis_date']} 的分析"
        )

        # 更新最终报告部分
        for section in message_buffer.report_sections.keys():
            if section in final_state:
                message_buffer.update_report_section(section, final_state[section])

        # 显示完整的最终报告
        display_complete_report(final_state)

        update_display(layout)


# Typer命令：分析
@app.command()
def analyze():
    # 运行分析
    run_analysis()


if __name__ == "__main__":
    app()
