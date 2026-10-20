from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MCPToolRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class EnterpriseToolMeta:
    name: str
    description: str
    risk_level: MCPToolRiskLevel = MCPToolRiskLevel.LOW
    read_only: bool = True
    required_roles: list[str] = field(default_factory=list)


@dataclass
class EnterpriseToolCallLog:
    tool_name: str
    arguments: dict[str, Any]
    success: bool
    result: Any = None
    error_message: str | None = None
    user_id: str = "anonymous"
    tenant_id: str = "tenant_001"
    confirmed: bool = False


@dataclass
class EnterpriseResourceMeta:
    uri: str
    title: str
    description: str
    mime_type: str = "text/markdown"
    required_roles: list[str] = field(default_factory=list)


@dataclass
class EnterprisePromptMeta:
    name: str
    title: str
    description: str
    arguments: list[str] = field(default_factory=list)