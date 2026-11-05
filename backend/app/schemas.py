"""Pydantic 请求/响应模型（接口出入参的结构定义）。"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


# ---------- 用户 ----------
class UserRegister(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    role: str
    created_at: datetime


class ChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=128)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------- 会话 ----------
class SessionCreate(BaseModel):
    title: str = "新会话"


class SessionRename(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    created_at: datetime
    updated_at: datetime


# ---------- 消息 / 问答 ----------
class Source(BaseModel):
    """一个引用片段：来自哪个文档 + 原文 + 相关度得分。"""
    doc_name: str
    content: str
    score: Optional[float] = None


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: str
    content: str
    sources: Optional[list[Source]] = None
    created_at: datetime


class ChatRequest(BaseModel):
    session_id: int
    question: str = Field(..., min_length=1)


# ---------- 知识库文档 ----------
class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    filename: str
    file_type: str
    chunk_count: int
    status: str
    size: int
    created_at: datetime
