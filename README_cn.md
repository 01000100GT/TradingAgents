<p align="center">
  <img src="assets/TauricResearch.png" style="width: 60%; height: auto;">
</p>

<div align="center" style="line-height: 1;">
  <a href="https://arxiv.org/abs/2412.20138" target="_blank"><img alt="arXiv" src="https://img.shields.io/badge/arXiv-2412.20138-B31B1B?logo=arxiv"/></a>
  <a href="https://discord.com/invite/hk9PGKShPK" target="_blank"><img alt="Discord" src="https://img.shields.io/badge/Discord-TradingResearch-7289da?logo=discord&logoColor=white&color=7289da"/></a>
  <a href="./assets/wechat.png" target="_blank"><img alt="微信" src="https://img.shields.io/badge/WeChat-TauricResearch-brightgreen?logo=wechat&logoColor=white"/></a>
  <a href="https://x.com/TauricResearch" target="_blank"><img alt="X 关注" src="https://img.shields.io/badge/X-TauricResearch-white?logo=x&logoColor=white"/></a>
  <br>
  <a href="https://github.com/TauricResearch/" target="_blank"><img alt="社区" src="https://img.shields.io/badge/Join_GitHub_Community-TauricResearch-14C290?logo=discourse"/></a>
</div>

<div align="center">
  <!-- 保留这些链接。翻译将随 README 自动更新。 -->
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=de">Deutsch</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=es">Español</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=fr">français</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ja">日本語</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ko">한국어</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=pt">Português</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ru">Русский</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=zh">中文</a>
</div>

---

# TradingAgents：多智能体 LLM 金融交易框架

> 🎉 **TradingAgents** 正式发布！我们收到了许多关于这项工作的咨询，感谢社区的热情。
>
> 因此，我们决定完全开源该框架。期待与您一起构建有影响力的项目！

<div align="center">
<a href="https://www.star-history.com/#TauricResearch/TradingAgents&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date" />
   <img alt="TradingAgents Star History" src="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date" style="width: 80%; height: auto;" />
 </picture>
</a>
</div>

<div align="center">

🚀 [TradingAgents](#tradingagents-框架) | ⚡ [安装与 CLI](#安装与-cli) | 🎬 [演示](https://www.youtube.com/watch?v=90gr5lwjIho) | 📦 [包使用](#tradingagents-包) | 🤝 [贡献](#贡献) | 📄 [引用](#引用)

</div>

## TradingAgents 框架

TradingAgents 是一个多智能体交易框架，它模仿了现实世界交易公司的动态。通过部署专门的 LLM 驱动的智能体：从基本面分析师、情绪专家和技术分析师，到交易员、风险管理团队，该平台协同评估市场状况并为交易决策提供信息。此外，这些智能体还进行动态讨论以确定最佳策略。

<p align="center">
  <img src="assets/schema.png" style="width: 100%; height: auto;">
</p>

> TradingAgents 框架专为研究目的而设计。交易表现可能因多种因素而异，包括所选的骨干语言模型、模型温度、交易周期、数据质量以及其他非确定性因素。[它不作为财务、投资或交易建议。](https://tauric.ai/disclaimer/)

我们的框架将复杂的交易任务分解为专门的角色。这确保了系统能够以稳健、可扩展的方式进行市场分析和决策。

### 分析师团队
- 基本面分析师：评估公司财务和业绩指标，识别内在价值和潜在危险信号。
- 情绪分析师：使用情绪评分算法分析社交媒体和公众情绪，以衡量短期市场情绪。
- 新闻分析师：监控全球新闻和宏观经济指标，解读事件对市场状况的影响。
- 技术分析师：利用技术指标（如 MACD 和 RSI）检测交易模式并预测价格走势。

<p align="center">
  <img src="assets/analyst.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

### 研究员团队
- 由看涨和看跌研究员组成，他们批判性地评估分析师团队提供的见解。通过结构化辩论，他们在潜在收益与固有风险之间取得平衡。

<p align="center">
  <img src="assets/researcher.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

### 交易员智能体
- 综合分析师和研究员的报告以做出明智的交易决策。它根据全面的市场洞察力确定交易的时机和规模。

<p align="center">
  <img src="assets/risk.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

### 风险管理和投资组合经理
- 通过评估市场波动性、流动性和其他风险因素，持续评估投资组合风险。风险管理团队评估和调整交易策略，向投资组合经理提供评估报告以供最终决策。
- 投资组合经理批准/拒绝交易提案。如果获得批准，订单将被发送到模拟交易所并执行。

<p align="center">
  <img src="assets/trader.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

## 安装与 CLI

### 安装

克隆 TradingAgents：
```bash
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
```

在您喜欢的任何环境管理器中创建一个虚拟环境：
```bash
conda create -n tradingagents python=3.13
conda activate tradingagents
```

安装依赖项：
```bash
pip install -r requirements.txt
```

### 所需 API

您还需要 FinnHub API 来获取财务数据。我们所有的代码都是用免费套餐实现的。
```bash
export FINNHUB_API_KEY=$YOUR_FINNHUB_API_KEY
```

您将需要 OpenAI API 用于所有智能体。
```bash
export OPENAI_API_KEY=$YOUR_OPENAI_API_KEY
```

### CLI 用法

您也可以直接通过运行以下命令来尝试 CLI：
```bash
python -m cli.main
```
您将看到一个屏幕，您可以在其中选择所需的股票代码、日期、LLM、研究深度等。

<p align="center">
  <img src="assets/cli/cli_init.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

一个界面将会出现，显示加载时的结果，让您跟踪智能体运行时的进度。

<p align="center">
  <img src="assets/cli/cli_news.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

<p align="center">
  <img src="assets/cli/cli_transaction.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

## TradingAgents 包

### 实现细节

我们使用 LangGraph 构建 TradingAgents，以确保灵活性和模块化。我们使用 `o1-preview` 和 `gpt-4o` 作为我们实验的深度思考和快速思考 LLM。但是，出于测试目的，我们建议您使用 `o4-mini` 和 `gpt-4.1-mini` 以节省成本，因为我们的框架会进行**大量** API 调用。

### Python 用法

要在您的代码中使用 TradingAgents，您可以导入 `tradingagents` 模块并初始化一个 `TradingAgentsGraph()` 对象。`.propagate()` 函数将返回一个决策。您可以运行 `main.py`，这里还有一个快速示例：

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())

# 正向传播
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

您还可以调整默认配置以设置您自己选择的 LLM、辩论轮次等。

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 创建自定义配置
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4.1-nano"  # 使用不同的模型
config["quick_think_llm"] = "gpt-4.1-nano"  # 使用不同的模型
config["max_debate_rounds"] = 1  # 增加辩论轮次
config["online_tools"] = True # 使用在线工具或缓存数据

# 使用自定义配置初始化
ta = TradingAgentsGraph(debug=True, config=config)

# 正向传播
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

> 对于 `online_tools`，我们建议在实验中启用它们，因为它们可以访问实时数据。智能体的离线工具依赖于我们 **Tauric TradingDB** 中的缓存数据，这是我们用于回溯测试的精选数据集。我们目前正在完善这个数据集，并计划在即将推出的项目中尽快发布它。敬请关注！

您可以在 `tradingagents/default_config.py` 中查看完整的配置列表。

## 贡献

我们欢迎社区的贡献！无论是修复错误、改进文档还是建议新功能，您的投入都有助于使这个项目变得更好。如果您对这一研究领域感兴趣，请考虑加入我们的开源金融 AI 研究社区 [Tauric Research](https://tauric.ai/)。

## 引用

如果您发现 *TradingAgents* 对您有所帮助，请引用我们的工作 :)

```
@misc{xiao2025tradingagentsmultiagentsllmfinancial,
      title={TradingAgents: Multi-Agents LLM Financial Trading Framework}, 
      author={Yijia Xiao and Edward Sun and Di Luo and Wei Wang},
      year={2025},
      eprint={2412.20138},
      archivePrefix={arXiv},
      primaryClass={q-fin.TR},
      url={https://arxiv.org/abs/2412.20138}, 
}
```