from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.faiss import dependable_faiss_import
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

load_dotenv()

_DATA_DIR = Path(__file__).resolve().parent / "data"
FAISS_PATH = _DATA_DIR / "faiss_index"
TOSS_FAQ_CSV_PATH = _DATA_DIR / "toss_faq_data.csv"


class TossFaqDocument(Document):
    def __init__(self, row: pd.Series):
        super().__init__(
            page_content=row.title,
            metadata={
                "id": row.id,
                "title": row.title,
                "description_text": row.description_text,
                "source_category_id": row.source_category_id,
                "category_set": row.category_set,
                "tag_set": row.tag_set,
                "tag_names": row.tag_names,
            },
        )


class TossFaqStore:
    _embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    _distance_strategy = DistanceStrategy.MAX_INNER_PRODUCT

    def __init__(self) -> None:
        self.store = self._load_faiss_store()

    def search(self, query: str, k: int = 10, threshold: float = 0.5):
        """
        3. reranker로 top 3~5 최종 선택
        """
        documents = self.store.similarity_search_with_score(
            query, k=k, score_threshold=threshold
        )
        return documents

    def _load_faiss_store(self) -> FAISS:
        faiss = dependable_faiss_import()
        if FAISS_PATH.exists():
            try:
                store = FAISS.load_local(
                    str(FAISS_PATH),
                    self._embeddings,
                    allow_dangerous_deserialization=True,
                    distance_strategy=self._distance_strategy,
                )
                if (
                    getattr(store.index, "metric_type", None)
                    != faiss.METRIC_INNER_PRODUCT
                ):
                    return self._create_faiss_store()
                return store
            except Exception as e:
                print(f"Error loading FAISS store: {e}")
                return self._create_faiss_store()
        return self._create_faiss_store()

    def _create_faiss_store(self):
        df = pd.read_csv(TOSS_FAQ_CSV_PATH)
        documents = []
        for index, row in df.iterrows():
            documents.append(TossFaqDocument(row))
        store = FAISS.from_documents(
            documents, self._embeddings, distance_strategy=self._distance_strategy
        )
        store.save_local(str(FAISS_PATH))
        return store
