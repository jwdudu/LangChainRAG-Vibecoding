"""Chroma 向量库：存向量并做相似度检索。"""
from langchain_chroma import Chroma
from ..config import settings
from .embeddings import get_embeddings

COLLECTION_NAME = "ecommerce_kb"


def get_vectorstore() -> Chroma:
    """获取（或创建）持久化的 Chroma 向量库。"""
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=settings.chroma_persist_dir,
    )
