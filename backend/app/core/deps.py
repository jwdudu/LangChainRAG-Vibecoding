"""FastAPI 依赖：当前用户解析与权限校验（RBAC）。"""
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from .security import decode_token

# 从请求头 Authorization: Bearer <token> 中提取令牌
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """解析 JWT 得到当前登录用户；未登录/令牌失效抛 401。"""
    if credentials is None:
        raise HTTPException(status_code=401, detail="未登录")
    username = decode_token(credentials.credentials)
    if username is None:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """仅管理员可访问，否则抛 403。"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可访问")
    return user
