from dataclasses import asdict

from app.deepagents_subagent.orchestrator import MainAgentOrchestrator
from app.deepagents_subagent.workspace import SubAgentWorkspace


class DeepAgentsSubAgentService:
    def __init__(self):
        self.workspace = SubAgentWorkspace()
        self.orchestrator = MainAgentOrchestrator(
            workspace=self.workspace
        )

    def list_subagents(self) -> list[dict]:
        return [
            asdict(item)
            for item in self.orchestrator.list_subagents()
        ]

    def run(
        self,
        user_goal: str,
    ) -> dict:
        result = self.orchestrator.run(
            user_goal=user_goal
        )

        return asdict(result)

    def run_parallel_simulation(
        self,
        user_goal: str,
    ) -> dict:
        result = self.orchestrator.run_parallel_simulation(
            user_goal=user_goal
        )

        return asdict(result)

    def list_files(self) -> list[str]:
        return self.workspace.list_files()

    def read_file(
        self,
        file_path: str,
    ) -> str:
        return self.workspace.read_file(file_path)

    def clear_workspace(self) -> None:
        self.workspace.clear()


deepagents_subagent_service = DeepAgentsSubAgentService()