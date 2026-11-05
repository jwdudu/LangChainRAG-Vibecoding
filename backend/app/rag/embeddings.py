"""本地 BGE 向量模型（懒加载单例，避免重复加载大模型）。"""
from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings
from ..config import settings


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    """加载本地 BGE 模型，把文字转成向量。首次调用会下载模型到本地缓存。"""
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model,
        model_kwargs={"device": settings.embedding_device},
        encode_kwargs={"normalize_embeddings": True},
    )
