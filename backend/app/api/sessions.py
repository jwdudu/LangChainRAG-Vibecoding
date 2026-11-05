"""会话与消息接口：多用户多会话管理 + 历史消息加载。"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from ..database import get_db
from ..models import User, Session as SessionModel, Message
from ..schemas import SessionCreate, SessionRename, SessionOut, MessageOut, Source
from ..core.deps import get_current_user

router = APIRouter(prefix="/api/sessions", tags=["会话"])


def _get_session_or_404(db: DBSession, session_id: int, user: User) -> SessionModel:
    """取会话并校验归属权：不存在抛 404，不属于当前用户抛 403。"""
    s = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if s is None:
        raise HTTPException(status_code=404, detail="会话不存在")
    if s.user_id != user.id:
        raise HTTPException(status_code=403, detail="无权访问该会话")
    return s


def _to_message_out(m: Message) -> MessageOut:
    """把数据库里的消息转成响应对象（含解析 sources JSON）。"""
    sources = None
    if m.sources:
        try:
            sources = [Source(**s) for s in json.loads(m.sources)]
        except (json.JSONDecodeError, TypeError):
            sources = None
    return MessageOut(id=m.id, role=m.role, content=m.content, sources=sources, created_at=m.created_at)


@router.get("", response_model=list[SessionOut])
def list_sessions(db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    """当前用户的会话列表，按最近更新排序。"""
    return (
        db.query(SessionModel)
        .filter(SessionModel.user_id == user.id)
        .order_by(SessionModel.updated_at.desc())
        .all()
    )


@router.post("", response_model=SessionOut)
def create_session(data: SessionCreate, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    """新建会话。"""
    s = SessionModel(user_id=user.id, title=data.title)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@router.patch("/{session_id}", response_model=SessionOut)
def rename_session(
    session_id: int, data: SessionRename, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)
):
    """重命名会话。"""
    s = _get_session_or_404(db, session_id, user)
    s.title = data.title
    db.commit()
    db.refresh(s)
    return s


@router.delete("/{session_id}")
def delete_session(session_id: int, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    """删除会话（级联删除其下消息）。"""
    s = _get_session_or_404(db, session_id, user)
    db.delete(s)
    db.commit()
    return {"message": "删除成功"}


@router.get("/{session_id}/messages", response_model=list[MessageOut])
def list_messages(session_id: int, db: DBSession = Depends(get_db), user: User = Depends(get_current_user)):
    """加载某会话的历史消息（登录后可找回历史对话）。"""
    _get_session_or_404(db, session_id, user)
    msgs = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.id.asc())
        .all()
    )
    return [_to_message_out(m) for m in msgs]
