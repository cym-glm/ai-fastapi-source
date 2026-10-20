from app.mcp_intro.service import mcp_intro_service


def main():
    manifest = mcp_intro_service.get_manifest()

    print("server:")
    print(manifest["server"])

    print("=" * 80)
    print("tools:")
    for tool in manifest["tools"]:
        print(tool)

    print("=" * 80)
    print("resources:")
    for resource in manifest["resources"]:
        print(resource)

    print("=" * 80)
    print("prompts:")
    for prompt in manifest["prompts"]:
        print(prompt)


if __name__ == "__main__":
    main()