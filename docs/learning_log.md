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

运行方式：

```bash
python days/day14_config_env.py