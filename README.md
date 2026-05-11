# LLM Agent Workbench

这是一个面向大模型 Agent 工程实践的学习项目。

项目目标是从零构建一个支持多轮对话、记忆管理、工具调用、RAG 和 API 服务的大模型 Agent 系统。

## 当前进度

目前已完成第一阶段基础模块：

- 多模型统一调用封装：`LLMClient`
- 项目配置管理：`AppConfig`
- JSON 对话记忆
- SQLite 对话记忆
- 长对话总结记忆
- 项目模块化重构
- FastAPI 聊天接口
- API smoke test

## 技术栈

- Python
- FastAPI
- Pydantic
- SQLite
- Ollama
- OpenAI-compatible API
- python-dotenv
- requests

## 项目结构

```text
LLM-Agent-Workbench/
├── days/                 # 每日学习脚本
├── examples/             # 示例和测试脚本
├── src/                  # 正式项目源码
│   ├── api/              # FastAPI 接口
│   ├── config/           # 配置管理
│   ├── llm/              # 大模型调用
│   ├── memory/           # 记忆模块
│   ├── tools/            # 工具调用模块
│   └── agent/            # Agent 核心逻辑
├── docs/                 # 文档和学习日志
├── requirements.txt
├── .env.example
└── README.md