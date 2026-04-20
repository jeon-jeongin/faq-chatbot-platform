from typing import Literal

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]

    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {"role": "user", "content": "모임 통장으로 자동이체가 가능한가요?"}
                ]
            }
        }


class ChatSource(BaseModel):
    id: int
    question: str
    answer: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]
    elapsed: float
    status: Literal["ok", "error"]
