from fastapi import Header, HTTPException, status
from app.schemas.user import CurrentUser, UserRole

async def get_current_user(
        x_user_id: str | None = Header(default=None),
        x_username: str | None = Header(default=None),
) -> CurrentUser:
    if not x_user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing x_user_id")
    
    if not x_username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing username")
    
    return CurrentUser(user_id=x_user_id, username=x_username, role=UserRole.USER, is_active=True)