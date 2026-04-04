from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from .service import ask

router = APIRouter(prefix="/toss_faq", tags=["toss_faq"])


class ChatRequest(BaseModel):
    input: str


class ChatSource(BaseModel):
    id: str
    question: str
    answer: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]
    elapsed: float
    status: Literal["ok", "error"]


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    result = ask(request.input)
    return ChatResponse(**result)
