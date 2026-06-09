Agent Stage Summary

本阶段完成了从 LLM 调用到基础 Agent 的核心链路。

当前已完成模块

### 1. Config

位置：

```text
src/config/settings.py

作用：

读取 .env
创建 AppConfig
校验模型配置
隐藏敏感信息

输入：

.env 环境变量

输出：

AppConfig 对象

### 2. LLMClient

位置：

src/llm/client.py

作用：

统一封装 Ollama / OpenAI-compatible API 调用
构造 messages
提供统一的 chat() 方法

输入：

user_message
system_prompt
history

输出：

模型回答字符串
3. Memory

位置：

src/memory/sqlite_memory.py
src/memory/summary_memory.py

作用：

SQLiteChatMemory 保存短期对话历史
SummaryMemory 保存长期摘要
长对话过长时压缩旧消息

输入：

user / assistant 消息

输出：

最近历史消息
长期摘要文本
4. Tools

位置：

src/tools/

当前工具：

CalculatorTool
FileReaderTool
TodoTool

作用：

CalculatorTool：计算数学表达式
FileReaderTool：安全读取项目目录内文件
TodoTool：管理任务列表

统一要求：

name
description
run()
ToolResult
5. ToolRegistry

位置：

src/tools/registry.py

作用：

注册工具
查询工具
通过工具名统一调用工具

输入：

tool_name
tool_input

输出：

ToolResult
6. ToolRouter

位置：

src/tools/router.py

作用：

根据用户自然语言判断是否需要工具
提取工具名和工具输入

示例：

帮我算一下 123 * 456
↓
tool_name = calculator
tool_input = 123 * 456

当前限制：

规则版 Router
依赖关键词和正则
对复杂任务泛化能力有限
7. BasicAgent

位置：

src/agent/basic_agent.py

作用：

串联 LLMClient、Memory、ToolRouter
判断是否调用工具
保存对话记忆
8. ReActAgent

位置：

src/agent/react_agent.py

作用：

引入 Thought / Action / Observation / Final Answer
让工具调用过程可观察
为 Trace 和多步 Agent 做准备
9. AgentTraceLogger

位置：

src/agent/trace.py

作用：

保存 Agent 执行过程
使用 JSONL 记录每次 Trace
方便调试、复盘和面试展示
10. MultiStepAgent

位置：

src/agent/multistep_agent.py

作用：

支持简单多步任务
当前主要实现：读取文件 → 总结文件

当前限制：

仍然是规则式多步任务
不能覆盖无限多种复杂需求
后续需要 Planner / Executor 解决泛化问题
当前 Agent 执行链路
用户输入
  ↓
ToolRouter 判断是否需要工具
  ↓
ToolRegistry 调用具体工具
  ↓
工具返回 ToolResult
  ↓
LLMClient 组织最终回答
  ↓
Memory 保存对话
  ↓
Trace 记录执行过程
当前项目的主要问题
1. 多步任务不能靠 if / elif 无限扩展

当前 MultiStepAgent 只能手写少数任务类型。

后续需要：

Planner
Executor

来解决动态任务拆解和执行问题。

2. ToolRouter 还是规则版

当前 Router 依赖关键词和正则。

后续可以升级成：

LLM Router
LLM Planner
3. 还没有 RAG

当前 Agent 可以读文件，但不能做知识库检索。

后续需要：

Document Loader
Text Splitter
Embedding
Vector Store
Retriever
RAG Chain
下一阶段计划
Day31：Planner 入门
Day32：Executor 执行器
Day33：Planner + Executor + Tools 整合
Day34：进入 RAG 阶段
当前阶段总结

本阶段完成了一个基础 Agent 工程雏形：

LLM 调用
配置管理
短期记忆
长期摘要记忆
工具系统
工具注册表
工具路由器
Basic Agent
ReAct Agent
Trace 日志
简单多步任务

它已经具备了 Agent 项目的基本骨架，但还需要 Planner / Executor 和 RAG 才能进一步接近真实大模型应用项目。