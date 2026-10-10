import uuid

from fastapi import Depends, Query

from app.dependencies.auth import get_current_user
from app.schemas.user import CurrentUser


class AgentContext:
    def __init__(
        self,
        current_user: CurrentUser,
        trace_id: str,
        debug: bool,
    ):
        self.current_user = current_user
        self.trace_id = trace_id
        self.debug = debug


async def get_agent_context(
    current_user: CurrentUser = Depends(get_current_user),
    debug: bool = Query(default=False, description="是否开启调试模式"),
) -> AgentContext:
    return AgentContext(
        current_user=current_user,
        trace_id=f"trace_{uuid.uuid4().hex[:8]}",
        debug=debug,
    )

