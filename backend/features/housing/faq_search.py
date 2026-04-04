from __future__ import annotations

from typing import Any

from config import settings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

_VECTORSTORE_CACHE: dict[str, FAISS] = {}


def _dataset_key(faq_data: list[dict]) -> str:
    # FAQ 데이터는 거의 고정이므로 id 시퀀스로 캐싱 키를 만든다.
    return "|".join(str(item.get("id", "")) for item in faq_data)


def _build_documents(faq_data: list[dict]) -> list[Document]:
    documents: list[Document] = []
    for faq in faq_data:
        documents.append(
            Document(
                page_content=(
                    f"질문: {faq['question']}\n답변: {faq['answer']}"
                ),
                metadata={
                    "id": faq["id"],
                    "question": faq["question"],
                    "answer": faq["answer"],
                },
            )
        )
    return documents


def _get_vectorstore(faq_data: list[dict]) -> FAISS:
    key = _dataset_key(faq_data)
    if key in _VECTORSTORE_CACHE:
        return _VECTORSTORE_CACHE[key]

    # settings에서 읽은 API 키를 명시적으로 넘겨서,
    # 환경변수 export 없이도 임베딩이 동작하도록 한다.
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=settings.openai_api_key,
    )
    documents = _build_documents(faq_data)
    vectorstore = FAISS.from_documents(documents, embeddings)
    _VECTORSTORE_CACHE[key] = vectorstore
    return vectorstore


def search_faq(
    faq_data: list[dict],
    query: str,
    top_k: int = 3,
) -> list[dict[str, Any]]:
    """
    week02 RAG 파이프라인 스타일:
    - FAQ를 문서로 구성
    - 임베딩 + FAISS similarity_search_with_score로 top_k retrieval
    """
    if not query.strip():
        return []

    vectorstore = _get_vectorstore(faq_data)
    results_with_score = vectorstore.similarity_search_with_score(query, k=top_k)

    formatted: list[dict[str, Any]] = []
    for doc, score in results_with_score:
        faq = {
            "id": doc.metadata.get("id"),
            "question": doc.metadata.get("question"),
            "answer": doc.metadata.get("answer"),
        }
        formatted.append({"faq": faq, "score": float(score)})

    return formatted


def format_context(search_results: list[dict]) -> str:
    if not search_results:
        return "관련 FAQ가 없습니다."

    # LLM이 출처를 구분하기 쉬우도록 FAQ id를 함께 포함한다.
    return "\n---\n".join(
        f"[{result['faq']['id']}] 질문: {result['faq']['question']}\n답변: {result['faq']['answer']}"
        for result in search_results
    )
