# pi-claw

`pi-claw` 是一个从零实现的轻量级 Agent 项目，用来学习和验证 Coding Agent 的核心机制：LLM 调用、会话状态、工具调用、事件流、Skill 加载以及简单 CLI/TUI 交互。

项目目标不是封装一个复杂框架，而是用尽量少的代码把 Agent 运行时讲清楚、跑起来，并作为后续扩展成个人 Coding Agent 的基础。

## 特性

- 极简 Node / Flow 抽象，帮助理解 workflow、chatbot 和 agent 的关系
- 基于 OpenAI-compatible API 的 LLM 调用
- 支持多轮会话与 JSONL 会话持久化
- 支持 read、write、edit、bash、grep、find、ls、search 等工具
- 支持 Skill 渐进式加载
- 提供 CLI 与简易 TUI 两种交互入口
- 本地运行数据默认写入 `.openclaw/`，不会提交到仓库

## 快速开始

### 1. 安装依赖

项目使用 `uv` 管理 Python 环境：

```bash
uv sync
```

### 2. 配置模型环境变量

默认读取 OpenAI-compatible 接口：

```bash
export OPENAI_API_KEY="你的 API Key"
export OPENAI_BASE_URL="你的 Base URL"
```

如果你使用兼容 OpenAI Chat Completions 的服务，只需要替换上面的两个环境变量即可。

### 3. 运行 CLI

```bash
uv run python cli.py
```

恢复已有会话：

```bash
uv run python cli.py --resume
```

指定会话名：

```bash
uv run python cli.py --session demo
```

### 4. 运行 TUI

```bash
uv run python tui.py
```

## 项目结构

```text
pi-claw/
├── agent/                 # Agent 运行时、会话、事件、设置、上下文加载
├── core/                  # LLM 调用与 Node/Flow 基础抽象
├── tools/                 # 工具定义、执行器、Skill 加载
├── examples/              # chatbot、workflow、tool agent 示例
├── cli.py                 # CLI 入口
├── tui.py                 # 简易 TUI 入口
├── pyproject.toml         # 项目配置
└── README.md
```

## 核心概念

### Workflow

Workflow 可以理解为多个 Node 串联起来的执行流程：

```text
输入 -> Node A -> Node B -> 输出
```

### Chatbot

Chatbot 是带循环的 workflow：

```text
用户输入 -> LLM -> 输出 -> 等待下一轮输入
```

### Agent

Agent 是带工具调用能力的 chatbot：

```text
用户输入 -> LLM 判断是否需要工具 -> 执行工具 -> 继续推理 -> 输出
```

### Skill

Skill 是一种本地能力的渐进式加载方式。相比把所有工具说明一次性塞进 prompt，Skill 更适合把复杂能力拆成可按需读取、按需执行的本地模块。

## 本地数据

运行时会产生本地会话和配置数据，例如：

```text
.openclaw/
```

## 会话压缩

`pi-claw` 支持最小版 session compaction。对话消息数超过阈值后，旧消息会被总结成一条 summary，并保留最近几条原始消息继续对话。

可以在 `.openclaw/settings.json` 中配置：

```json
{
  "compact_enabled": true,
  "compact_max_messages": 30,
  "compact_keep_recent_messages": 10
}
```

## 开发检查

运行基础语法检查：

```bash
uv run python -m compileall agent core tools examples cli.py tui.py
```

## 设计原则

- 少即是多：优先保留最小可理解实现
- CLI 优先：先让 runtime 和事件流稳定，再做更复杂界面
- 工具克制：优先使用 read、write、edit、bash 等少量通用工具
- 可观察：Agent 的每一步通过事件流暴露，便于调试和扩展

## License

见 [LICENSE](./LICENSE)。
