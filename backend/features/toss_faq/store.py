from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

load_dotenv()


_DATA_DIR = Path(__file__).resolve().parent / "data"
TITLE_INDEX_PATH = _DATA_DIR / "faiss_title"
FULL_INDEX_PATH = _DATA_DIR / "faiss_full"
CSV_PATH = _DATA_DIR / "toss_faq_data.csv"


class TitleDocument(Document):
    def __init__(self, row):
        super().__init__(
            page_content=row.title,
            metadata={"id": row.id},
        )


class FullDocument(Document):
    def __init__(self, row):
        super().__init__(
            page_content=f"{row.title} {row.description_text} 관련 주제: {row.tag_names}",
            metadata={
                "id": row.id,
                "title": row.title,
                "answer": row.description_text,
                "tag_names": row.tag_names,
            },
        )


class BM25Document(Document):
    def __init__(self, row):
        super().__init__(
            page_content=f"{row.title} {row.description_text} {row.tag_names}",
            metadata={"id": row.id},
        )


class TossFaqStore:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.title_store = self._load_or_create(TITLE_INDEX_PATH, TitleDocument)
        self.full_store = self._load_or_create(FULL_INDEX_PATH, FullDocument)
        self.bm25_retriever = self._create_bm25()
        self.full_doc_map = {
            doc.metadata["id"]: doc for doc in self.full_store.docstore._dict.values()
        }

    def search_and_get_context(self, query: str, k: int = 5):
        reranked_docs = self.search(query, k)
        return "\n---\n".join([doc["answer"] for doc in reranked_docs])

    def search(self, query: str, k: int = 5):
        query_vec = self.embeddings.embed_query(query)
        bm25_docs = self.bm25_retriever.invoke(query)
        title_vec_docs = self.title_store.similarity_search_with_score_by_vector(
            query_vec, k=k
        )
        full_vec_docs = self.full_store.similarity_search_with_score_by_vector(
            query_vec, k=k
        )
        reranked_docs = self._rerank(bm25_docs, title_vec_docs, full_vec_docs)
        return reranked_docs

    def _rerank(self, bm25_docs, title_vec_docs, full_vec_docs):
        threshold = 0.5
        ret = {}  # candidates = {}
        for doc in bm25_docs:
            weight = 0.1
            ret[doc.metadata["id"]] = {"score": weight, "bm25": weight}
        for doc, score in title_vec_docs:
            score *= 0.7
            doc_id = doc.metadata["id"]
            ret_doc = ret.get(doc_id)
            if ret_doc:
                ret_doc["score"] += score
                ret_doc["title_score"] = score
            else:
                ret[doc_id] = {"score": score, "title_score": score}
        for doc, score in full_vec_docs:
            score *= 0.2
            doc_id = doc.metadata["id"]
            ret_doc = ret.get(doc_id)
            if ret_doc:
                ret_doc["score"] += score
                ret_doc["full_score"] = score
            else:
                ret[doc_id] = {"score": score, "full_score": score}
        ret = [
            {
                **doc,
                "id": doc_id,
                "question": self.full_doc_map[doc_id].metadata["title"],
                "answer": self.full_doc_map[doc_id].metadata["answer"],
            }
            for doc_id, doc in ret.items()
            if doc["score"] >= threshold
        ]
        return sorted(ret, key=lambda x: x["score"], reverse=True)

    def _load_or_create(self, path, doc_cls):
        if path.exists():
            return FAISS.load_local(
                str(path),
                self.embeddings,
                allow_dangerous_deserialization=True,
                distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT,
            )
        df = pd.read_csv(CSV_PATH)
        docs = [doc_cls(row) for _, row in df.iterrows()]
        store = FAISS.from_documents(
            docs,
            self.embeddings,
            distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT,
            normalize_L2=True,
        )
        store.save_local(str(path))
        return store

    def _create_bm25(self):
        df = pd.read_csv(CSV_PATH)
        docs = [BM25Document(row=row) for _, row in df.iterrows()]
        retriever = BM25Retriever.from_documents(docs)
        retriever.k = 5
        return retriever


store = TossFaqStore()
