"""问答接口：RAG 检索 + 大模型流式生成（SSE），回答附带引用片段。"""
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session as DBSession
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from ..database import get_db, SessionLocal
from ..models import User, Session as SessionModel, Message
from ..schemas import ChatRequest, Source
from ..core.deps import get_current_user
from ..config import settings
from ..rag.chain import get_llm, build_context, SYSTEM_PROMPT
from ..rag.retriever import retrieve

router = APIRouter(prefix="/api/chat", tags=["问答"])


def _sse(payload: dict) -> str:
    """把一个字典编码成一条 SSE 消息。"""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.post("")
async def chat(
    data: ChatRequest,
    db: DBSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # 校验会话归属权
    session = db.query(SessionModel).filter(SessionModel.id == data.session_id).first()
    if session is None or session.user_id != user.id:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 保存用户提问
    user_msg = Message(session_id=data.session_id, role="user", content=data.question)
    db.add(user_msg)
    db.commit()

    # 取历史消息（多轮对话上下文，排除刚写入的这条）
    history = (
        db.query(Message)
        .filter(Message.session_id == data.session_id, Message.id != user_msg.id)
        .order_by(Message.id.asc())
        .all()
    )

    # 检索相关片段（CPU 计算放到线程池，避免阻塞事件循环）
    docs, scores = await run_in_threadpool(retrieve, data.question, settings.top_k)
    context = build_context(docs)
    sources = [
        Source(
            doc_name=d.metadata.get("source", "未知"),
            content=d.page_content,
            score=round(s, 4),
        ).model_dump()
        for d, s in zip(docs, scores)
    ]

    # 组织消息：系统提示词 + 最近 10 条历史 + 当前问题
    history_msgs = []
    for m in history[-10:]:
        if m.role == "user":
            history_msgs.append(HumanMessage(content=m.content))
        elif m.role == "assistant":
            history_msgs.append(AIMessage(content=m.content))
    msgs = [SystemMessage(content=SYSTEM_PROMPT.format(context=context)), *history_msgs, HumanMessage(content=data.question)]

    llm = get_llm()

    async def event_stream():
        parts = []
        try:
            async for chunk in llm.astream(msgs):
                text = chunk.content if isinstance(chunk.content, str) else ""
                if text:
                    parts.append(text)
                    yield _sse({"type": "delta", "content": text})
        except Exception as e:
            yield _sse({"type": "error", "message": f"生成失败: {e}"})
            return

        answer = "".join(parts)

        # 落库：保存回答 + 更新会话标题（用新会话时的首个问题）
        db2 = SessionLocal()
        try:
            db2.add(
                Message(
                    session_id=data.session_id,
                    role="assistant",
                    content=answer,
                    sources=json.dumps(sources, ensure_ascii=False),
                )
            )
            s = db2.query(SessionModel).filter(SessionModel.id == data.session_id).first()
            if s is not None and s.title == "新会话":
                s.title = data.question[:20]
            db2.commit()
        finally:
            db2.close()

        yield _sse({"type": "done", "sources": sources})

    # 性能优化：流式生成前释放数据库连接，避免 LLM 流式期间(5~15秒)占着连接池、导致其他请求排队超时
    db.close()

    return StreamingResponse(event_stream(), media_type="text/event-stream")
