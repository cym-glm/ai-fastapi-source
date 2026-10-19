from pathlib import Path

from app.deepagents_core.schemas import DeepAgentState


class InMemoryDeepAgentBackend:
    """
    教学版 Backend。

    功能：
    1. 按 thread_id 保存 state。
    2. 支持读写虚拟文件。
    3. 模拟 checkpointer + workspace。
    """

    def __init__(self):
        self.states: dict[str, DeepAgentState] = {}

    def get_state(
        self,
        thread_id: str,
    ) -> DeepAgentState:
        if thread_id not in self.states:
            self.states[thread_id] = DeepAgentState()

        return self.states[thread_id]

    def save_state(
        self,
        thread_id: str,
        state: DeepAgentState,
    ) -> None:
        self.states[thread_id] = state

    def write_file(
        self,
        thread_id: str,
        path: str,
        content: str,
    ) -> None:
        state = self.get_state(thread_id)
        state.files[path] = content
        self.save_state(thread_id, state)

    def read_file(
        self,
        thread_id: str,
        path: str,
    ) -> str:
        state = self.get_state(thread_id)

        if path not in state.files:
            raise FileNotFoundError(
                f"文件不存在：{path}"
            )

        return state.files[path]

    def list_files(
        self,
        thread_id: str,
    ) -> list[str]:
        state = self.get_state(thread_id)
        return list(state.files.keys())


class LocalFilesystemDeepAgentBackend:
    """
    教学版本地文件 Backend。

    注意：
    仅建议本地开发使用。
    生产环境要做用户隔离、路径限制和安全审计。
    """

    def __init__(
        self,
        root_dir: str = "data/deepagents_core_workspace",
    ):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(
            parents=True,
            exist_ok=True,
        )
        self.memory_backend = InMemoryDeepAgentBackend()

    def _thread_dir(
        self,
        thread_id: str,
    ) -> Path:
        safe_thread_id = thread_id.replace("/", "_")
        path = self.root_dir / safe_thread_id
        path.mkdir(
            parents=True,
            exist_ok=True,
        )
        return path

    def get_state(
        self,
        thread_id: str,
    ) -> DeepAgentState:
        return self.memory_backend.get_state(thread_id)

    def save_state(
        self,
        thread_id: str,
        state: DeepAgentState,
    ) -> None:
        self.memory_backend.save_state(thread_id, state)

    def write_file(
        self,
        thread_id: str,
        path: str,
        content: str,
    ) -> None:
        state = self.get_state(thread_id)
        state.files[path] = content
        self.save_state(thread_id, state)

        target = self._thread_dir(thread_id) / path.lstrip("/")
        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        target.write_text(
            content,
            encoding="utf-8",
        )

    def read_file(
        self,
        thread_id: str,
        path: str,
    ) -> str:
        target = self._thread_dir(thread_id) / path.lstrip("/")

        if target.exists():
            return target.read_text(
                encoding="utf-8",
            )

        return self.memory_backend.read_file(
            thread_id,
            path,
        )

    def list_files(
        self,
        thread_id: str,
    ) -> list[str]:
        thread_dir = self._thread_dir(thread_id)

        disk_files = [
            "/" + str(file.relative_to(thread_dir))
            for file in thread_dir.rglob("*")
            if file.is_file()
        ]

        memory_files = self.memory_backend.list_files(thread_id)

        return sorted(
            set(disk_files + memory_files)
        )