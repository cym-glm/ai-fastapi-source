from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ResearchTaskStatus(str, Enum):
    CREATED = "created"
    PLANNING = "planning"
    RESEARCHING = "researching"
    ANALYZING = "analyzing"
    WRITING = "writing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchStepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class ResearchSourceType(str, Enum):
    WEB = "web"
    ENTERPRISE_KB = "enterprise_kb"
    USER_FILE = "user_file"
    MEMORY = "memory"
    GENERATED = "generated"


class ResearchSubAgentRole(str, Enum):
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    WRITER = "writer"
    REVIEWER = "reviewer"


@dataclass
class ResearchSource:
    source_id: str
    source_type: ResearchSourceType
    title: str
    content: str
    url: str | None = None
    file_path: str | None = None
    score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchPlanStep:
    step_id: str
    title: str
    description: str
    owner: ResearchSubAgentRole | None = None
    status: ResearchStepStatus = ResearchStepStatus.PENDING
    output_file: str | None = None
    result_summary: str | None = None
    error_message: str | None = None


@dataclass
class ResearchPlan:
    plan_id: str
    topic: str
    objective: str
    steps: list[ResearchPlanStep]
    dimensions: list[str] = field(default_factory=list)


@dataclass
class ResearchNote:
    note_id: str
    topic: str
    key_points: list[str]
    sources: list[ResearchSource]
    output_file: str | None = None


@dataclass
class AnalysisResult:
    analysis_id: str
    findings: list[str]
    risks: list[str]
    opportunities: list[str]
    recommendations: list[str]
    output_file: str | None = None


@dataclass
class ReviewResult:
    review_id: str
    passed: bool
    issues: list[str]
    suggestions: list[str]
    output_file: str | None = None


@dataclass
class DeepResearchRequest:
    topic: str
    objective: str = "输出一份结构化研究报告"
    tenant_id: str = "tenant_001"
    user_id: str = "anonymous"
    max_sources: int = 8
    include_enterprise_kb: bool = True
    include_web: bool = True


@dataclass
class DeepResearchResult:
    task_id: str
    thread_id: str
    status: ResearchTaskStatus
    topic: str
    plan: ResearchPlan
    final_answer: str
    sources: list[ResearchSource]
    files: list[str]
    trace: list[str]
    review: ReviewResult | None = None
    error_message: str | None = None