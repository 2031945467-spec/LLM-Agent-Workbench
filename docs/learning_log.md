# Learning Log

## Day13: 多模型统一调用封装

目标：

- 封装统一的 LLMClient
- 支持本地 Ollama 模型
- 预留云端 API 接口
- 为后续 Agent、Memory、RAG 做准备

核心收获：

- 学会使用 `.env` 管理模型配置
- 理解了 provider 的作用
- 学会把 Ollama 和 OpenAI 调用封装到统一接口
- 理解了 messages 是多轮对话的核心结构
- 为后续 Memory、Tools、Agent、RAG 做了底层准备




## Day14: 环境变量与配置管理

今天完成了 AppConfig 配置管理模块。

核心收获：

- 理解了 `.env` 的作用
- 学会使用 `load_dotenv()` 加载环境变量
- 学会用 `os.getenv()` 读取配置
- 学会用 `dataclass` 封装项目配置
- 学会对配置进行 validate 校验
- 学会隐藏 API Key，避免敏感信息泄露
- 理解了统一配置入口对工程项目的重要性


## Day15: JSON 对话记忆

今天完成了 JsonChatMemory，对话历史可以保存到本地 JSON 文件。

核心收获：

- 理解了大模型本身不会自动记住历史
- 学会把 user / assistant 消息保存成 JSON
- 学会从 JSON 文件加载历史消息
- 学会把历史 messages 传给 LLMClient
- 理解了 Memory 模块在 Agent 中的作用
- 理解了为什么要限制传入模型的历史条数

## Day16: SQLite 对话记忆

今天完成了 SQLiteChatMemory，把对话历史从 JSON 文件升级为 SQLite 数据库。

核心收获：

- 理解了 JSON Memory 和 SQLite Memory 的区别
- 学会使用 sqlite3 连接数据库
- 学会创建 messages 数据表
- 学会用 SQL 插入 user / assistant 消息
- 学会查询最近 N 条历史消息
- 理解了 session_id 对多会话记忆的作用
- 理解了数据库记忆更适合真实 Agent 项目

## Day17: 长对话总结记忆

今天完成了 SummaryMemory，实现了“短期记忆 + 长期摘要记忆”的组合。

核心收获：

- 理解了为什么不能无限传入完整历史消息
- 学会把较早的历史消息压缩成 summary
- 学会保留最近几条消息作为短期记忆
- 理解了长期记忆和短期记忆的区别
- 理解了 Agent 记忆模块中的上下文压缩思想

## Day18: 项目模块化重构

今天把前几天的学习脚本迁移到了 `src/` 正式项目目录中。

核心收获：

- 理解了 `days/` 和 `src/` 的区别
- 学会把配置管理迁移到 `src/config/settings.py`
- 学会把大模型调用迁移到 `src/llm/client.py`
- 学会把 SQLite 记忆迁移到 `src/memory/sqlite_memory.py`
- 学会把长期摘要记忆迁移到 `src/memory/summary_memory.py`
- 理解了正式项目中模块之间的依赖关系
- 学会使用 `python -m examples.day18_project_chat` 运行模块化项目


## Day19: FastAPI 聊天接口

今天把命令行聊天升级成了 FastAPI 后端接口。

核心收获：

- 学会使用 FastAPI 定义 HTTP 接口
- 学会用 Pydantic 定义请求体和响应体
- 学会把 LLMClient、SQLiteChatMemory、SummaryMemory 组合进 API
- 理解了 `/chat` 接口的完整流程
- 理解了 session_id 对多会话记忆隔离的作用
- 理解了从命令行程序到后端服务的项目升级方式

## Day20: 阶段总结与项目包装

今天完成了第一阶段的阶段性整理。

核心收获：

- 理解了 README 对项目展示的重要性
- 学会编写 API smoke test 脚本
- 学会用 requests 自动测试 FastAPI 接口
- 梳理了当前项目结构
- 理解了 `days/` 和 `src/` 的区别
- 理解了项目从学习脚本走向工程项目的过程
- 修复了 FastAPI 路由路径和 Pydantic 响应模型参数传递问题

## Day21: Calculator Tool

今天开始进入工具调用阶段，实现了第一个工具 `CalculatorTool`。

核心收获：

- 理解了 Tool 是 Agent 可调用的能力模块
- 学会用 `ToolResult` 统一表示工具执行结果
- 学会把计算器能力封装成 `CalculatorTool`
- 理解了为什么不能直接对用户输入使用 `eval()`
- 初步理解了 Agent 后续如何调用工具完成任务

## Day22: File Reader Tool

今天实现了第二个工具 `FileReaderTool`，用于安全读取项目目录内的文本文件。

核心收获：

- 理解了文件读取也可以封装成 Agent Tool
- 学会使用 `pathlib.Path` 处理文件路径
- 学会限制工具只能读取项目目录内的文件
- 学会限制可读取的文件类型和文件大小
- 理解了工具安全对 Agent 系统的重要性
- 为后续文档总结、RAG 和 Agent 工具调用做准备

## Day23: Todo Tool

今天实现了第三个工具 `TodoTool`，用于管理任务列表。

核心收获：

- 理解了任务管理也可以封装成 Agent Tool
- 学会使用 JSON 文件保存工具状态
- 学会设计 add / list / done / delete / clear 等工具命令
- 继续强化了 `ToolResult` 统一返回格式
- 理解了工具需要有统一入口 `run()`
- 为后续 Tool Router 和 Agent 工具调用做准备

## Day24: Tool Registry

今天实现了 `ToolRegistry`，用于统一注册和调用多个工具。

核心收获：

- 理解了为什么需要工具注册表
- 学会把 CalculatorTool、FileReaderTool、TodoTool 统一管理
- 学会通过工具名称调用工具
- 理解了工具统一接口 `run()` 的意义
- 理解了 ToolRegistry 是后续 Agent 调用工具的基础

## Day25: Tool Router

今天实现了 `ToolRouter`，可以根据用户自然语言判断是否需要调用工具。

核心收获：

- 理解了 ToolRegistry 和 ToolRouter 的区别
- 学会把自然语言映射成 tool_name + tool_input
- 学会用规则和正则表达式做简单工具路由
- 理解了 Agent 调用工具前需要先完成意图判断
- 为后续 Agent 基础版做准备

## Day26: Basic Agent

今天实现了基础版 Agent，把 LLMClient、Memory、ToolRouter 和 ToolRegistry 串联起来。

核心收获：

- 理解了 Agent 不只是聊天，而是会判断是否需要调用工具
- 学会把自然语言输入交给 ToolRouter 做工具路由
- 学会用 ToolRegistry 调用具体工具
- 学会把工具返回结果交给 LLM 整理成自然语言回答
- 学会把 Agent 对话保存到 SQLiteChatMemory
- 理解了 BasicAgent 是后续 ReAct Agent 的基础
