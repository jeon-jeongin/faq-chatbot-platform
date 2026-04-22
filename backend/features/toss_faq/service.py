import time
from enum import Enum
from logging import getLogger

from config import settings
from langchain_core.messages import AIMessage, HumanMessage
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
Answer user questions using the provided FAQ context and conversation history.

## Critical Rules

1. Grounding
- For factual answers about Toss products or policies, use the provided FAQ context first.
- For meta questions about the conversation itself, such as summarizing the chat or recalling a previous user question, use the conversation history.
- If the FAQ context is empty or irrelevant, you may use only the conversation history, but only for information that already appeared in the chat.
- Do NOT use prior knowledge.
- Do NOT assume or infer beyond the FAQ context or conversation history.

2. No Hallucination
- If the answer is not in the FAQ context or conversation history, say you cannot find it.
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

8. Conversation Memory
- Treat the conversation history as a reliable source only for what was already said in the chat.
- If the user asks "what was my first question?" or "summarize our conversation", answer from the history without claiming new product facts.
- If a follow-up question refers to something previously discussed, use the history to understand what "that" refers to, then answer with FAQ context when available.

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
1. 토스 상품/정책에 대한 사실 설명은 컨텍스트를 우선 사용하세요.
2. 사용자가 이전 대화 요약, 첫 질문 회상, 방금 한 말 정리처럼 대화 자체를 묻는 경우에는 history를 사용하세요.
3. 후속 질문에서 "그거", "그럼", "지금까지 대화"처럼 앞 문맥을 가리키면 history를 참고해 질문 의도를 이해하세요.
4. FAQ 컨텍스트나 history에 없는 내용은 절대 추측하지 마세요.
5. 관련 정보가 없다면, 찾을 수 없다고 안내해주세요.

답변은 토스 스타일의 친근한 해요체로 작성해주세요."""


class FaqService:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name=settings.default_model, api_key=settings.openai_api_key
        )
        self.parser = StrOutputParser()
        self.store = store

    def build_history(self, messages: list[ChatMessage]):
        """메시지 히스토리에 대한 LangChain 메시지 객체 리스트를 반환합니다."""
        history = []

        for message in messages[:-1]:
            if message.role == "user":
                history.append(HumanMessage(content=message.content))
            elif message.role == "assistant":
                history.append(AIMessage(content=message.content))

        return history

    def invoke(self, messages: list[ChatMessage]) -> dict:
        prompt_template = self.get_prompt_template()
        question = messages[-1].content
        history = self.build_history(messages)
        retrieved = self.store.search_and_get_context(question)
        chain = RunnableParallel(
            answer=prompt_template | self.llm | self.parser,
            sources=RunnableLambda(lambda x: x["sources"]),
        )
        return chain.invoke(
            {
                "history": history,
                "context": retrieved["context"],
                "question": question,
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
