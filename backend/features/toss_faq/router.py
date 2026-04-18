from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from .service import ask

router = APIRouter(prefix="/toss_faq", tags=["toss_faq"])


class ChatRequest(BaseModel):
    input: str

    # 클래스 내부에 설정하는 방법
    class Config:
        json_schema_extra = {
            "example": {"input": "모임 통장으로 자동이체가 가능한가요?"}
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


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Toss FAQ 챗봇 서비스 API
    """
    result = ask(request.input)
    return ChatResponse(**result)
