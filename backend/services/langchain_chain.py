from functools import lru_cache

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from config import settings


@lru_cache(maxsize=8)
def build_answer_chain(system_prompt: str):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", "{question}"),
        ]
    )
    llm = ChatOpenAI(
        model=settings.default_model,
        temperature=0,
        api_key=settings.openai_api_key,
    )
    return prompt | llm | StrOutputParser()
