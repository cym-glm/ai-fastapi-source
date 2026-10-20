from pathlib import Path


class DeepResearchWorkspace:
    def __init__(
        self,
        root_dir: str = "data/deep_research_workspace",
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
        target = self.root_dir / file_path.lstrip("/")
        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        target.write_text(
            content,
            encoding="utf-8",
        )
        return str(target)

    def read_file(
        self,
        file_path: str,
    ) -> str:
        target = self.root_dir / file_path.lstrip("/")

        if not target.exists():
            raise FileNotFoundError(
                f"文件不存在：{target}"
            )

        return target.read_text(
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