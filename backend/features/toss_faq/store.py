from pathlib import Path

from dotenv import load_dotenv
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

load_dotenv()

_DATA_DIR = Path(__file__).resolve().parent / "data"
FAISS_PATH = _DATA_DIR / "faiss_index"
TOSS_FAQ_CSV_PATH = _DATA_DIR / "toss_faq_data.csv"


class TossFaqDocument(Document):
    def __init__(self, row: pd.Series):
        super().__init__(
            page_content=row.description_text,
            metadata={
                "id": row.id,
                "title": row.title,
                "source_category_id": row.source_category_id,
                "category_set": row.category_set,
                "tag_set": row.tag_set,
                "tag_names": row.tag_names,
            },
        )


class TossFaqStore:
    _embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    def __init__(self) -> None:
        self.store = self._load_faiss_store()

    def _load_faiss_store(self) -> FAISS:
        if FAISS_PATH.exists():
            try:
                return FAISS.load_local(
                    str(FAISS_PATH),
                    self._embeddings,
                    allow_dangerous_deserialization=True,
                )
            except Exception as e:
                print(f"Error loading FAISS store: {e}")
                return self._create_faiss_store()
        return self._create_faiss_store()

    def _create_faiss_store(self):
        df = pd.read_csv(TOSS_FAQ_CSV_PATH)
        documents = []
        for index, row in df.iterrows():
            documents.append(TossFaqDocument(row))
        store = FAISS.from_documents(documents, self._embeddings)
        store.save_local(str(FAISS_PATH))
        return store

    def search(self, query: str, k: int = 5) -> list[Document]:
        """
        1. cosine 기준으로 top_k = 10~20
        2. threshold = 0.7 정도로 1차 필터
        3. reranker로 top 3~5 최종 선택
        cosine 기반 추천 (normalize + IP)
        threshold는 0.75 전후에서 시작
        하지만 진짜 중요한 건 👉 reranking
        """
        pass
