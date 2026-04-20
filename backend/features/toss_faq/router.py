from fastapi import APIRouter

from .schema import ChatRequest, ChatResponse
from .service import ask

router = APIRouter(prefix="/toss_faq", tags=["toss_faq"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Toss FAQ 챗봇 서비스 API
    """
    result = ask(request.messages)
    return ChatResponse(**result)
