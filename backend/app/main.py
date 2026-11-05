"""FastAPI 应用入口。"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import Base, engine, SessionLocal
from .models import User
from .core.security import hash_password
from .api import auth, sessions, users, kb, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时：建表 + 初始化内置管理员账号 admin/123456。"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == "admin").first() is None:
            db.add(User(username="admin", password_hash=hash_password("123456"), role="admin"))
            db.commit()
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

# 开发环境放开跨域；生产环境应改成具体前端域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(users.router)
app.include_router(kb.router)
app.include_router(chat.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.app_name}
