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

运行方式：

```bash
python days/day13_llm_client.py