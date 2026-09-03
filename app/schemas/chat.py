
from pydantic import BaseModel, Field, field_validator

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500, description="Message to be sent" )
    model: str = Field("gpt-3.5-turbo", description="Model to use")
    temprature: float = Field(0.5, description="Temperature for the model")
    stream: bool = Field(False, description="Stream the response")
    @field_validator("model")
    @classmethod
    def validate_model(cls, v):
        supported_models = ["gpt-3.5-turbo", "gpt-4", "deepseek-chat", "qwen-72e"]
        if v not in supported_models:
            raise ValueError (f"Unsupported model: {v}")
        return v

class ChatResponse(BaseModel):
    answer: str = Field(..., description="Response from the model")
    model: str = Field(..., description="Model used")
