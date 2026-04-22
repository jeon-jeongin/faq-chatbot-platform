from fastapi import APIRouter, HTTPException

from .schema import ChatRequest, ChatResponse, ChatSourceDetail
from .service import ask, get_source_detail

router = APIRouter(prefix="/toss_faq", tags=["toss_faq"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Toss FAQ 챗봇 서비스 API
    """
    result = ask(request.messages)
    return ChatResponse(**result)


@router.get("/sources/{doc_id}", response_model=ChatSourceDetail)
async def source_detail(doc_id: int) -> ChatSourceDetail:
    """
    선택한 FAQ 근거의 상세 HTML 내용을 조회하는 API
    """
    result = get_source_detail(doc_id)
    if not result:
        raise HTTPException(status_code=404, detail="FAQ source not found")
    return ChatSourceDetail(**result)
