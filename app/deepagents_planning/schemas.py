from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PlanStepStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class PlanStepType(str, Enum):
    THINK = "think"
    TOOL = "tool"
    SUBAGENT = "subagent"
    WRITE_FILE = "write_file"
    REVIEW = "review"
    FINAL = "final"


class PlanningTaskType(str, Enum):
    RESEARCH = "research"
    REPORT = "report"
    CODE_ANALYSIS = "code_analysis"
    DATA_ANALYSIS = "data_analysis"
    GENERAL = "general"


@dataclass
class PlanStep:
    step_id: str
    title: str
    description: str
    step_type: PlanStepType
    status: PlanStepStatus = PlanStepStatus.PENDING
    dependencies: list[str] = field(default_factory=list)
    tool_name: str | None = None
    tool_input: dict[str, Any] = field(default_factory=dict)
    subagent_name: str | None = None
    output_file: str | None = None
    result: str | None = None
    error_message: str | None = None
    retry_count: int = 0
    max_retries: int = 1


@dataclass
class DeepPlan:
    plan_id: str
    task_type: PlanningTaskType
    user_goal: str
    steps: list[PlanStep]
    summary: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PlanObservation:
    step_id: str
    success: bool
    output: str
    error_message: str | None = None
    need_replan: bool = False


@dataclass
class PlanExecutionTrace:
    event: str
    step_id: str | None = None
    message: str = ""


@dataclass
class PlanRunResult:
    plan_id: str
    user_goal: str
    final_answer: str
    steps: list[PlanStep]
    files: list[str]
    trace: list[PlanExecutionTrace]