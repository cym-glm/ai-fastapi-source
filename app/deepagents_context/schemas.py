from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ContextSource(str, Enum):
    SYSTEM = "system"
    USER = "user"
    MESSAGE = "message"
    PLAN = "plan"
    TOOL_RESULT = "tool_result"
    FILE = "file"
    SUBAGENT = "subagent"
    RAG = "rag"
    MEMORY = "memory"
    TRACE = "trace"


class ContextPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ContextPlacement(str, Enum):
    ACTIVE_CONTEXT = "active_context"
    WORKSPACE_FILE = "workspace_file"
    MEMORY = "memory"
    STORE = "store"
    TRACE_ONLY = "trace_only"
    DROPPED = "dropped"


@dataclass
class ContextItem:
    item_id: str
    source: ContextSource
    priority: ContextPriority
    content: str
    title: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    estimated_tokens: int = 0
    placement: ContextPlacement = ContextPlacement.ACTIVE_CONTEXT
    file_path: str | None = None
    summary: str | None = None


@dataclass
class ContextBudget:
    max_tokens: int = 4000
    reserved_for_system: int = 500
    reserved_for_user_goal: int = 500
    reserved_for_answer: int = 800

    @property
    def available_tokens(self) -> int:
        return max(
            0,
            self.max_tokens
            - self.reserved_for_system
            - self.reserved_for_user_goal
            - self.reserved_for_answer,
        )


@dataclass
class ContextPack:
    system_context: str
    user_goal: str
    active_items: list[ContextItem]
    offloaded_items: list[ContextItem]
    dropped_items: list[ContextItem]
    total_estimated_tokens: int
    warnings: list[str] = field(default_factory=list)

    def to_prompt(self) -> str:
        lines = [
            "# System Context",
            self.system_context,
            "",
            "# User Goal",
            self.user_goal,
            "",
            "# Selected Context",
        ]

        for item in self.active_items:
            lines.append("")
            lines.append(f"## {item.title or item.item_id}")
            lines.append(f"source: {item.source.value}")
            lines.append(f"priority: {item.priority.value}")

            if item.file_path:
                lines.append(f"file_path: {item.file_path}")

            lines.append("")
            lines.append(item.summary or item.content)

        if self.offloaded_items:
            lines.append("")
            lines.append("# Offloaded Context Pointers")

            for item in self.offloaded_items:
                lines.append(
                    f"- {item.title or item.item_id}: {item.file_path}"
                )

        if self.warnings:
            lines.append("")
            lines.append("# Warnings")

            for warning in self.warnings:
                lines.append(f"- {warning}")

        return "\n".join(lines)


@dataclass
class SubAgentContextResult:
    agent_name: str
    task: str
    summary: str
    output_file: str
    warnings: list[str] = field(default_factory=list)


@dataclass
class ContextRunResult:
    user_goal: str
    context_pack: ContextPack
    prompt_preview: str
    files: list[str]
    trace: list[str]