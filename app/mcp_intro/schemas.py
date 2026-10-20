from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class MCPPrimitiveType(str, Enum):
    TOOL = "tool"
    RESOURCE = "resource"
    PROMPT = "prompt"


@dataclass
class MCPTool:
    name: str
    description: str
    input_schema: dict[str, Any]
    func: Callable[..., Any]
    read_only: bool = True
    dangerous: bool = False


@dataclass
class MCPResource:
    uri: str
    name: str
    description: str
    mime_type: str
    content: str


@dataclass
class MCPPrompt:
    name: str
    description: str
    arguments: list[str]
    template: str


@dataclass
class MCPToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass
class MCPToolResult:
    name: str
    success: bool
    result: Any = None
    error_message: str | None = None


@dataclass
class MCPServerInfo:
    name: str
    version: str
    description: str
    capabilities: list[MCPPrimitiveType] = field(default_factory=list)


@dataclass
class MCPServerManifest:
    server: MCPServerInfo
    tools: list[dict[str, Any]]
    resources: list[dict[str, Any]]
    prompts: list[dict[str, Any]]


@dataclass
class MCPHostRunResult:
    user_request: str
    selected_tool: str | None
    tool_result: MCPToolResult | None
    final_answer: str
    trace: list[str] = field(default_factory=list)