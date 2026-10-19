from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class DeepTodoStatus(str, Enum):
    TODO = "todo"
    DOING = "doing"
    DONE = "done"
    FAILED = "failed"


@dataclass
class DeepTodo:
    todo_id: str
    title: str
    status: DeepTodoStatus = DeepTodoStatus.TODO
    result: str | None = None


@dataclass
class DeepAgentMessage:
    role: str
    content: str


@dataclass
class DeepAgentContext:
    tenant_id: str = "tenant_001"
    user_id: str = "anonymous"
    thread_id: str = "default_thread"
    task_id: str = "default_task"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DeepTool:
    name: str
    description: str
    func: Callable[..., str]
    requires_confirmation: bool = False


@dataclass
class DeepToolCall:
    tool_name: str
    arguments: dict[str, Any]


@dataclass
class DeepToolResult:
    tool_name: str
    output: str
    success: bool = True
    error_message: str | None = None


@dataclass
class DeepSubAgentSpec:
    name: str
    description: str
    system_prompt: str
    tools: list[DeepTool] = field(default_factory=list)


@dataclass
class DeepSubAgentResult:
    name: str
    task: str
    result: str
    success: bool = True

#  create_deep_agent 参数配置 
@dataclass
class DeepAgentConfig:
    name: str
    model: str
    system_prompt: str
    tools: list[DeepTool] = field(default_factory=list)
    subagents: list[DeepSubAgentSpec] = field(default_factory=list)
    debug: bool = False


@dataclass
class DeepAgentState:
    messages: list[DeepAgentMessage] = field(default_factory=list)
    todos: list[DeepTodo] = field(default_factory=list)
    files: dict[str, str] = field(default_factory=dict)
    trace: list[str] = field(default_factory=list)
    final_answer: str | None = None


@dataclass
class DeepAgentRunInput:
    messages: list[DeepAgentMessage]
    context: DeepAgentContext


@dataclass
class DeepAgentRunOutput:
    thread_id: str
    task_id: str
    final_answer: str
    todos: list[DeepTodo]
    files: list[str]
    trace: list[str]