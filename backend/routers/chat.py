from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from services.chatbot import ask


router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    domain: str
    question: str


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
    result = ask(request.domain, request.question)
    return ChatResponse(**result)


@router.get("/health")
async def chat_health():
    return {"status": "ok", "service": "chat"}
