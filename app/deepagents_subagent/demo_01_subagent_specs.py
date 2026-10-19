from dataclasses import asdict

from app.deepagents_subagent.agents import build_default_subagent_specs


def main():
    specs = build_default_subagent_specs()

    for spec in specs:
        print(asdict(spec))
        print("=" * 100)


if __name__ == "__main__":
    main()