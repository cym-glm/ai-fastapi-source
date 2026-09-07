from fastapi import Header, HTTPException, status,Depends
from app.schemas.user import CurrentUser, UserRole
from app.core.config import settings
from app.core.request_context import set_user_id


async def verfy_api_key(
        x_api_key: str | None = Header(default=None),
)->str:
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")
    if x_api_key != settings.app_api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")
    return x_api_key


async def get_current_user(
        api_key: str = Depends(verfy_api_key, use_cache=True), # use_cache=False 每次请求都重新验证
        x_user_id: str | None = Header(default=None),
        x_username: str | None = Header(default=None),
        x_user_role: str | None = Header(default="user"),
) -> CurrentUser:
    if not x_user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing x_user_id")
    
    if not x_username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing username")
    
    role = UserRole.ADMIN if x_user_role == "admin" else UserRole.USER
    set_user_id(x_user_id)
    return CurrentUser(user_id=x_user_id, username=x_username,  is_active=True, role=role)


# get_current_user---> verfy_api_key --读取header -- jwt-- 验证token--db



async def require_admin(
        current_user: CurrentUser = Depends(get_current_user)
    )->CurrentUser:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user