"""知识库管理接口（仅管理员可访问）。"""
import hashlib
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session as DBSession
from ..database import get_db
from ..models import User, Document
from ..schemas import DocumentOut
from ..core.deps import require_admin, get_current_user
from ..services.kb_service import process_document, delete_document_vectors
from ..services import suggestion_service

router = APIRouter(prefix="/api/kb", tags=["知识库"])

UPLOAD_DIR = Path("uploads")
ALLOWED_EXTS = {".pdf", ".txt", ".md", ".docx", ".csv", ".xlsx", ".xls"}


@router.post("/upload", response_model=DocumentOut)
def upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: DBSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """上传文档：立即返回，后台异步解析入库。"""
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {ext}")

    UPLOAD_DIR.mkdir(exist_ok=True)
    file_path = UPLOAD_DIR / f"{admin.id}_{file.filename}"

    content = file.file.read()
    size = len(content)
    hash_ = hashlib.sha256(content).hexdigest()
    with open(file_path, "wb") as f:
        f.write(content)

    doc = Document(
        filename=file.filename,
        file_type=ext.lstrip("."),
        size=size,
        hash=hash_,
        uploaded_by=admin.id,
        status="pending",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    background_tasks.add_task(process_document, doc.id, str(file_path))
    return doc


@router.get("/documents", response_model=list[DocumentOut])
def list_documents(db: DBSession = Depends(get_db), admin: User = Depends(require_admin)):
    """文档列表（按创建时间倒序）。"""
    return db.query(Document).order_by(Document.created_at.desc()).all()


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: int, db: DBSession = Depends(get_db), admin: User = Depends(require_admin)):
    """删除文档：同时清理数据库记录与向量库中的分块。"""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if doc is None:
        raise HTTPException(status_code=404, detail="文档不存在")
    delete_document_vectors(str(doc_id))
    db.delete(doc)
    db.commit()
    return {"message": "删除成功"}


@router.get("/suggestions")
def get_suggestions(db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    """返回问答页的示例问题（所有登录用户可用），知识库变化时自动重新生成。"""
    return suggestion_service.get_suggestions(db)
