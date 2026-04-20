import time
from enum import Enum
from logging import getLogger

from config import settings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnableParallel
from langchain_openai import ChatOpenAI

from .schema import ChatMessage
from .store import store

logger = getLogger(__name__)


class FaqPromptTemplates(Enum):
    SYSTEM_PROMPT = """You are a customer support assistant for Toss, a Korean fintech service.

## Goal
Answer user questions using ONLY the provided context.

## Critical Rules

1. Grounding
- Use ONLY the provided context to answer.
- Do NOT use prior knowledge.
- Do NOT assume or infer beyond the context.

2. No Hallucination
- If the answer is not in the context, say you cannot find it.
- NEVER fabricate information.

3. Context Handling
- If the context is irrelevant, treat it as missing.
- Focus only on relevant parts.

4. Tone & Language
- Always answer in Korean.
- Use a friendly and natural tone (해요체), like Toss.

5. Answer Style
- Start with a direct answer.
- Keep it concise and clear.
- Add short explanation only if needed.

6. Fallback Behavior
If information is missing:
- Clearly say you couldn't find it
- Suggest next steps (e.g., contact support)

7. Safety
- Do not provide financial/legal advice beyond context
- Do not guess user-specific account info

---

You must strictly follow these rules."""

    USER_PROMPT = """다음은 토스 FAQ에서 검색된 참고 정보예요:

[컨텍스트 시작]
{context}
[컨텍스트 끝]

사용자 질문:
{question}

---

지침:
1. 컨텍스트에서 질문과 관련된 정보를 찾으세요.
2. 찾은 정보만 사용해서 답변하세요.
3. 없는 내용은 절대 추측하지 마세요.
4. 관련 정보가 없다면, 찾을 수 없다고 안내해주세요.

답변은 토스 스타일의 친근한 해요체로 작성해주세요."""


class FaqService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name=settings.default_model, api_key=settings.openai_api_key
        )
        self.parser = StrOutputParser()
        self.store = store

    def invoke(self, messages: list[ChatMessage]) -> dict:
        prompt_template = self.get_prompt_template()
        input = messages[-1].content
        retrieved = self.store.search_and_get_context(input)
        chain = RunnableParallel(
            answer=prompt_template | self.llm | self.parser,
            sources=RunnableLambda(lambda x: x["sources"]),
        )
        return chain.invoke(
            {
                "context": retrieved["context"],
                "question": input,
                "sources": retrieved["sources"],
            }
        )

    def get_prompt_template(self):
        return ChatPromptTemplate.from_messages(
            [
                ("system", FaqPromptTemplates.SYSTEM_PROMPT.value),
                MessagesPlaceholder(variable_name="history"),
                ("human", FaqPromptTemplates.USER_PROMPT.value),
            ]
        )


faq_service = FaqService()


def ask(messages: list[ChatMessage]) -> dict:
    start = time.time()
    result = faq_service.invoke(messages)
    elapsed = time.time() - start
    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "elapsed": round(elapsed, 2),
        "status": "ok",
    }
