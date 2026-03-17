def search_faq(faq_data: list[dict], query: str, top_k: int = 3) -> list[dict]:
    query_words = query.split()
    scored = []

    for faq in faq_data:
        score = sum(1 for keyword in faq["keywords"] if keyword in query)
        score += sum(1 for word in query_words if word in faq["question"])
        if score > 0:
            scored.append({"faq": faq, "score": score})

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:top_k]


def format_context(search_results: list[dict]) -> str:
    if not search_results:
        return "관련 FAQ가 없습니다."

    return "\n---\n".join(
        f"Q: {result['faq']['question']}\nA: {result['faq']['answer']}"
        for result in search_results
    )
