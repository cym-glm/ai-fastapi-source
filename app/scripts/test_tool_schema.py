
import json
from app.tools.registry import tool_registry



def main():
    tools = tool_registry.to_openai_tools()
    print(json.dumps(tools, ensure_ascii=False,  indent=2))


if __name__ == "__main__":
    main()