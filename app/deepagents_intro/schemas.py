from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TodoStatus(str, Enum):
    TODO = "todo"
    DOING = "doing"
    DONE = "done"
    FAILED = "failed"


@dataclass
class TodoItem:
    todo_id: str
    title: str
    status: TodoStatus = TodoStatus.TODO
    result: str | None = None


@dataclass
class AgentTask:
    task_id: str
    goal: str
    user_request: str
    todos: list[TodoItem] = field(default_factory=list)
    workspace_dir: str = "data/deepagents_workspace"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    tool_name: str
    input: str
    output: str
    success: bool = True


@dataclass
class SubAgentResult:
    agent_name: str
    task: str
    result: str
    success: bool = True


@dataclass
class DeepAgentRunResult:
    task_id: str
    goal: str
    todos: list[TodoItem]
    workspace_files: list[str]
    final_answer: str
    trace: list[str] = field(default_factory=list)