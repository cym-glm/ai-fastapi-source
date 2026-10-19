from pathlib import Path


class SubAgentWorkspace:
    def __init__(
        self,
        root_dir: str = "data/deepagents_subagent_workspace",
    ):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def write_file(
        self,
        file_path: str,
        content: str,
    ) -> str:
        path = self.root_dir / file_path.lstrip("/")
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            content,
            encoding="utf-8",
        )

        return str(path)

    def read_file(
        self,
        file_path: str,
    ) -> str:
        path = self.root_dir / file_path.lstrip("/")

        if not path.exists():
            raise FileNotFoundError(
                f"文件不存在：{path}"
            )

        return path.read_text(
            encoding="utf-8",
        )

    def list_files(self) -> list[str]:
        return [
            "/" + str(path.relative_to(self.root_dir))
            for path in self.root_dir.rglob("*")
            if path.is_file()
        ]

    def clear(self) -> None:
        for path in self.root_dir.rglob("*"):
            if path.is_file():
                path.unlink()