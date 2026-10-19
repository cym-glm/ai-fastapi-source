from pathlib import Path


class SimpleWorkspace:
    def __init__(
        self,
        root_dir: str = "data/deepagents_workspace",
    ):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def write_file(
        self,
        file_name: str,
        content: str,
    ) -> str:
        path = self.root_dir / file_name
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
        file_name: str,
    ) -> str:
        path = self.root_dir / file_name

        if not path.exists():
            raise FileNotFoundError(
                f"文件不存在：{path}"
            )

        return path.read_text(
            encoding="utf-8",
        )

    def list_files(self) -> list[str]:
        return [
            str(path.relative_to(self.root_dir))
            for path in self.root_dir.rglob("*")
            if path.is_file()
        ]

    def append_file(
        self,
        file_name: str,
        content: str,
    ) -> str:
        old_content = ""

        path = self.root_dir / file_name

        if path.exists():
            old_content = path.read_text(
                encoding="utf-8",
            )

        new_content = old_content + content

        return self.write_file(
            file_name=file_name,
            content=new_content,
        )