from enum import Enum
from pydantic import BaseModel, Field

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class CurrentUser(BaseModel):
    user_id: str = Field(...,  description="The user's unique identifier")
    username: str = Field(..., description="The user's username")
    role: UserRole = Field(default=UserRole.USER, decription="The user's role")
    is_active: bool = Field(default=True, alias="isActive", description="Whether the user is active or not")