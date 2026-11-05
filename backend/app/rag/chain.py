"""大模型与提示词：负责根据检索到的资料生成回答。"""
from functools import lru_cache
from langchain_openai import ChatOpenAI
from ..config import settings

SYSTEM_PROMPT = """你是一名专业的电商平台客服助手，负责回答用户关于商品的问题。

请严格遵守以下规则：
1. 只能依据下面【参考资料】中的内容回答商品相关问题，禁止编造资料中没有的信息。
2. 如果用户在询问你的能力（例如"你能做什么""你能帮我什么"），请友好地介绍自己：你是一名基于知识库的电商商品问答助手，可以帮用户查询商品信息、推荐尺码、解答退换货政策等问题，并邀请用户继续提问。
3. 对于商品相关问题，如果参考资料不足以回答，请明确说"根据现有知识库，暂时无法回答该问题"。
4. 回答中引用资料内容时，用 [1]、[2] 这样的编号标注出处。
5. 用中文回答，条理清晰、简洁专业。

【参考资料】
{context}"""


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    """通义千问（DashScope OpenAI 兼容端点），开启流式输出。"""
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.dashscope_api_key,
        base_url=settings.llm_base_url,
        temperature=settings.llm_temperature,
        streaming=True,
    )


def build_context(docs) -> str:
    """把检索到的片段拼成带编号的参考资料文本。"""
    parts = [f"[{i}] {doc.page_content}" for i, doc in enumerate(docs, start=1)]
    return "\n\n".join(parts)
