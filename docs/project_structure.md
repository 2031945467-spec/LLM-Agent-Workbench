# Project Structure

本项目采用学习脚本与正式源码分离的结构。

## 顶层结构

```text
LLM-Agent-Workbench/
├── days/
├── examples/
├── src/
├── docs/
├── data/
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore

## 快速开始

1. 克隆项目

```bash
git clone https://github.com/2031945467-spec/LLM-Agent-Workbench.git
cd LLM-Agent-Workbench
2. 创建虚拟环境
python -m venv .venv

Windows PowerShell:

.venv\Scripts\Activate.ps1
3. 安装依赖
pip install -r requirements.txt
4. 配置环境变量

复制 .env.example 为 .env，并修改配置：

LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2:0.5b

OPENAI_API_KEY=
OPENAI_BASE_URL=
OPENAI_MODEL=gpt-4o-mini

LLM_TEMPERATURE=0.7
APP_ENV=dev
DEBUG=true
5. 启动 API 服务
uvicorn src.api.main:app --reload

浏览器打开：

http://127.0.0.1:8000/docs
API 示例
健康检查
GET /health
聊天接口
POST /chat

请求体：

{
  "message": "我正在学习大模型 Agent。",
  "session_id": "study_agent",
  "max_history": 6
}
查看历史
GET /sessions/{session_id}/history
查看长期摘要
GET /sessions/{session_id}/summary
清空记忆
POST /sessions/{session_id}/clear
API 测试

先启动服务：

uvicorn src.api.main:app --reload

然后另开一个终端运行：

python -m examples.day20_api_smoke_test