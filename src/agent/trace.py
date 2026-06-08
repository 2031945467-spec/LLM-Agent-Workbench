"""
Agent Trace Logger

作用：
1. 保存 Agent 每次执行过程
2. 记录 user_input、answer、used_tool、steps
3. 使用 JSONL 格式保存日志
4. 方便后续调试、复盘和面试展示
"""

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from src.agent.react_agent import ReActResponse


class AgentTraceLogger:
    """
    Agent Trace 日志记录器。

    每次 Agent 执行后，把完整执行过程保存成一条 JSONL 记录。

    JSONL 格式：
        一行就是一条 JSON 记录。
    """

    def __init__(self, file_path: str = "data/agent_traces.jsonl") -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        user_input: str,
        response: ReActResponse,
    ) -> None:
        """
        保存一次 Agent 执行记录。
        """

        record = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "user_input": user_input,
            "answer": response.answer,
            "used_tool": response.used_tool,
            "tool_success": response.tool_success,
            "tool_result": response.tool_result,
            "steps": [asdict(step) for step in response.steps],
        }

        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    default=str,
                )
                + "\n"
            )

    def load_all(self) -> list[dict[str, Any]]:
        """
        读取全部 Trace 记录。
        """

        if not self.file_path.exists():
            return []

        records: list[dict[str, Any]] = []

        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        return records

    def load_recent(self, limit: int = 5) -> list[dict[str, Any]]:
        """
        读取最近 limit 条 Trace 记录。
        """

        records = self.load_all()

        return records[-limit:]

    def clear(self) -> None:
        """
        清空 Trace 日志。
        """

        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write("")

    def show_recent(self, limit: int = 5) -> None:
        """
        打印最近几条 Trace。
        """

        records = self.load_recent(limit=limit)

        if not records:
            print("当前没有 Agent Trace 记录。")
            return

        print(f"\n========== 最近 {len(records)} 条 Agent Trace ==========")

        for index, record in enumerate(records, start=1):
            print(f"\nTrace {index}")
            print(f"时间: {record.get('timestamp')}")
            print(f"用户输入: {record.get('user_input')}")
            print(f"是否使用工具: {record.get('used_tool')}")
            print(f"工具是否成功: {record.get('tool_success')}")
            print(f"最终回答: {record.get('answer')}")

            steps = record.get("steps", [])

            for step_index, step in enumerate(steps, start=1):
                print(f"\n  Step {step_index}")
                print(f"  Thought: {step.get('thought')}")
                print(f"  Action: {step.get('action')}")
                print(f"  Action Input: {step.get('action_input')}")
                print(f"  Observation: {step.get('observation')}")