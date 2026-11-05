"""问答页「示例问题」生成：根据知识库文档内容，用大模型生成自然的问题，并缓存。"""
import logging
from ..models import Document
from ..rag.chain import get_llm

logger = logging.getLogger(__name__)

# 固定展示的系统类问题（不依赖知识库，任何时候都能回答）
SYSTEM_QUESTIONS = ["你能帮我做什么？"]

# 模块级缓存：key 为文档文件名元组，value 为生成的知识库问题列表
_cache = {"key": None, "kb_questions": []}


def get_suggestions(db) -> dict:
    """返回示例问题：{system: [...], kb: [...]}。知识库变化时自动重新生成并缓存。"""
    filenames = tuple(sorted(d.filename for d in db.query(Document).all()))
    if _cache["key"] == filenames:
        return {"system": SYSTEM_QUESTIONS, "kb": _cache["kb_questions"]}

    topics = [f.rsplit(".", 1)[0] for f in filenames]  # 去掉扩展名当作主题
    _cache["key"] = filenames
    _cache["kb_questions"] = _generate_kb_questions(topics)
    return {"system": SYSTEM_QUESTIONS, "kb": _cache["kb_questions"]}


def _generate_kb_questions(topics: list[str]) -> list[str]:
    """用大模型根据文档主题生成自然的问题；失败时用模板兜底。"""
    if not topics:
        return []

    prompt = (
        "你是一个电商知识库问答系统。根据下面这些知识库文档的主题，"
        "生成 5 条用户最可能问的自然问题，每条一行，不要编号、不要解释、不要加引号：\n\n"
        + "\n".join(f"- {t}" for t in topics)
    )
    try:
        resp = get_llm().invoke(prompt)
        lines = []
        for line in str(resp.content).split("\n"):
            line = line.strip().lstrip("0123456789.-、) ").strip()
            if line:
                lines.append(line)
        if lines:
            return lines[:5]
    except Exception:
        logger.exception("生成示例问题失败，使用模板兜底")

    # 兜底：按文件名套模板
    return [f"关于「{t}」，你能帮我介绍一下吗？" for t in topics[:5]]
