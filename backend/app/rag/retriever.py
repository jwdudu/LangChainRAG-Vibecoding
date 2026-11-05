"""检索：从向量库召回与问题最相关的片段。

说明：当前为向量检索；后续「优化阶段」会在此扩展为
混合检索（向量 + BM25 + RRF 融合）与重排序（bge-reranker）。
"""
from ..config import settings
from .vectorstore import get_vectorstore


def retrieve(query: str, k: int | None = None):
    """向量检索，返回 (文档列表, 相关度得分列表)。"""
    k = k or settings.top_k
    docs_with_scores = get_vectorstore().similarity_search_with_relevance_scores(query, k=k)
    # 过滤掉相关度太低的片段，避免把无关内容塞给大模型、污染引用
    filtered = [(d, s) for d, s in docs_with_scores if s >= settings.min_relevance_score]
    docs = [d for d, _ in filtered]
    scores = [s for _, s in filtered]
    return docs, scores
