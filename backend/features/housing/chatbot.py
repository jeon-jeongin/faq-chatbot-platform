import time

from features.housing.faq_housing import FAQ_DATA, SYSTEM_PROMPT
from features.housing.faq_search import format_context, search_faq
from features.housing.langchain_chain import build_answer_chain


def validate_question(question: str) -> tuple[str | None, str]:
    stripped = question.strip() if question else ""

    if not stripped:
        return "질문을 입력해주세요.", stripped
    if len(stripped) < 2:
        return "질문이 너무 짧습니다.", stripped
    if len(stripped) > 500:
        return "500자 이내로 입력해주세요.", stripped
    if stripped.replace(" ", "").isdigit():
        return "주택청약 관련 질문을 입력해주세요.", stripped

    return None, stripped


def ask(domain: str, question: str) -> dict:
    error, normalized_question = validate_question(question)
    if error:
        return {
            "answer": error,
            "sources": [],
            "elapsed": 0.0,
            "status": "error",
        }

    if domain != "housing":
        return {
            "answer": "아직 지원하지 않는 도메인입니다. 현재는 housing만 사용할 수 있습니다.",
            "sources": [],
            "elapsed": 0.0,
            "status": "error",
        }

    try:
        start = time.time()
        results = search_faq(FAQ_DATA, normalized_question, top_k=3)
        context = format_context(results)
        answer_chain = build_answer_chain(SYSTEM_PROMPT)
        answer = answer_chain.invoke(
            {"context": context, "question": normalized_question}
        )

        sources = [
            {
                "id": result["faq"]["id"],
                "question": result["faq"]["question"],
                "answer": result["faq"]["answer"],
            }
            for result in results
        ]

        return {
            "answer": answer,
            "sources": sources,
            "elapsed": round(time.time() - start, 2),
            "status": "ok",
        }
    except Exception as exc:
        return {
            "answer": f"오류가 발생했습니다: {exc}",
            "sources": [],
            "elapsed": 0.0,
            "status": "error",
        }
