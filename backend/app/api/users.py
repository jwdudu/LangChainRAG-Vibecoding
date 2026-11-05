"""用户接口：当前用户信息 / 用户列表（管理员）。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession
from ..database import get_db
from ..models import User
from ..schemas import UserOut
from ..core.deps import get_current_user, require_admin

router = APIRouter(prefix="/api/users", tags=["用户"])


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    """获取当前登录用户信息。"""
    return user


@router.get("", response_model=list[UserOut])
def list_users(db: DBSession = Depends(get_db), _: User = Depends(require_admin)):
    """用户列表（仅管理员）。"""
    return db.query(User).order_by(User.id.asc()).all()
