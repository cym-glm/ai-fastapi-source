

from pydantic import BaseModel, ConfigDict, Field

class ChatAliasRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    session_id: str | None  = Field(..., alias="sessionId")
    user_id: str | None  = Field(..., alias="userId")
    mesage: str


request1 = ChatAliasRequest(
        sessionId="123456",
        userId="1234567890",
        mesage="Hello, this is a test message"
)

request2 = ChatAliasRequest(
    session_id="123456",
    user_id="1234567890",
    mesage="Hello, this is a test message"


)

print(request1.model_dump())
print(request1.model_dump(by_alias=True))
print(request2.model_dump())


