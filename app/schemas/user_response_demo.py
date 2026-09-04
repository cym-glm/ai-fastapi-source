from pydantic import BaseModel

# 数据库模型 
class UserInDB(BaseModel):
    user_id: str
    username: str
    email: str
    password_hash: str


# fastapi 响应模型 返回给前端的模型 
class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str


user = UserInDB(
    user_id="u_10001",
    username="dawei",
    email="dawei@example.com",
    password_hash="hashed_password_xxx"
)

response = UserResponse(
    user_id=user.user_id,
    username=user.username,
    email=user.email
)

print(response.model_dump())