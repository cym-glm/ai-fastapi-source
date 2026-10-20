from mcp.server import MCPServer

mcp = MCPServer("simple mcp server")

@mcp.tool()
def add (a: int, b: int) -> int:
    """两个数字相加。"""
    return a + b

@mcp.resource("greating://{name}")
def greating(name: str) -> str:
    """say hello to someone"""
    return f"hello {name}"


