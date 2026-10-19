from dataclasses import asdict

from app.deepagents_planning.executor import DeepPlanningExecutor
from app.deepagents_planning.planner import RuleBasedDeepPlanner
from app.deepagents_planning.schemas import DeepPlan, PlanRunResult
from app.deepagents_planning.workspace import PlanningWorkspace


class DeepAgentsPlanningService:
    def __init__(self):
        self.workspace = PlanningWorkspace()
        self.planner = RuleBasedDeepPlanner()
        self.executor = DeepPlanningExecutor(
            workspace=self.workspace
        )

    def create_plan(
        self,
        user_goal: str,
    ) -> dict:
        plan = self.planner.create_plan(
            user_goal
        )

        return self._plan_to_dict(plan)

    def run_goal(
        self,
        user_goal: str,
        allow_replan: bool = True,
    ) -> dict:
        result = self.executor.run_goal(
            user_goal=user_goal,
            allow_replan=allow_replan,
        )

        return self._result_to_dict(result)

    def run_plan(
        self,
        plan: DeepPlan,
        allow_replan: bool = True,
    ) -> dict:
        result = self.executor.run_plan(
            plan=plan,
            allow_replan=allow_replan,
        )

        return self._result_to_dict(result)

    def list_files(self) -> list[str]:
        return self.workspace.list_files()

    def read_file(
        self,
        file_path: str,
    ) -> str:
        return self.workspace.read_file(
            file_path
        )

    def clear_workspace(self) -> None:
        self.workspace.clear()

    def _plan_to_dict(
        self,
        plan: DeepPlan,
    ) -> dict:
        return asdict(plan)

    def _result_to_dict(
        self,
        result: PlanRunResult,
    ) -> dict:
        return asdict(result)


deepagents_planning_service = DeepAgentsPlanningService()