from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class SubAgentRole(str, Enum):
    RESEARCH = "research"
    ANALYSIS = "analysis"
    WRITER = "writer"
    REVIEWER = "reviewer"
    CODE = "code"
    DATA = "data"
    GENERAL = "general"


class SubAgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class SubAgentTool:
    name: str
    description: str
    func: Callable[..., str]
    read_only: bool = True
    requires_confirmation: bool = False


@dataclass
class SubAgentSpec:
    name: str
    role: SubAgentRole
    description: str
    system_prompt: str
    allowed_tools: list[str] = field(default_factory=list)
    output_format: str = "markdown"


@dataclass
class SubAgentTask:
    task_id: str
    agent_name: str
    instruction: str
    input_context: str = ""
    expected_output: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SubAgentResult:
    task_id: str
    agent_name: str
    role: SubAgentRole
    status: SubAgentStatus
    summary: str
    output: str
    output_file: str | None = None
    warnings: list[str] = field(default_factory=list)
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DelegationDecision:
    should_delegate: bool
    agent_name: str | None
    reason: str
    task_instruction: str = ""


@dataclass
class MainAgentRunResult:
    user_goal: str
    delegation_results: list[SubAgentResult]
    final_answer: str
    files: list[str]
    trace: list[str] = field(default_factory=list)