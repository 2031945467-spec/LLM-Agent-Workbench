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

