"""知识库入库与删除的底层处理逻辑。"""
import logging
from ..database import SessionLocal
from ..models import Document
from ..rag.loaders import load_file
from ..rag.splitter import get_splitter
from ..rag.vectorstore import get_vectorstore

logger = logging.getLogger(__name__)


def process_document(doc_id: int, file_path: str):
    """后台任务：解析 → 分块 → 向量化 → 存 Chroma，并更新文档状态。"""
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc is None:
            return
        doc.status = "processing"
        db.commit()

        raw_docs = load_file(file_path, doc.filename)
        chunks = get_splitter().split_documents(raw_docs)
        # 给每个分块打上文档 id 与文件名元数据（删除文档时按 doc_id 清理）
        for c in chunks:
            c.metadata["doc_id"] = str(doc_id)
            c.metadata["source"] = doc.filename

        get_vectorstore().add_documents(chunks)

        doc.chunk_count = len(chunks)
        doc.status = "done"
        db.commit()
    except Exception:
        logger.exception("文档入库失败 doc_id=%s", doc_id)
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc is not None:
            doc.status = "failed"
            db.commit()
    finally:
        db.close()


def delete_document_vectors(doc_id: str):
    """按 doc_id 元数据删除 Chroma 中该文档的所有分块。"""
    get_vectorstore()._collection.delete(where={"doc_id": doc_id})
