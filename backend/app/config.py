"""应用配置：从 .env 读取，未设置时使用默认值。"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # 应用
    app_name: str = "电商商品知识库 RAG 问答系统"
    secret_key: str = ""  # JWT 签名密钥，必须在 .env 里用随机值设置（SECRET_KEY）
    access_token_expire_minutes: int = 60 * 24 * 7  # 令牌有效期 7 天

    # 数据库（默认 SQLite，生产可换 PostgreSQL）
    database_url: str = "sqlite:///./rag.db"

    # 大模型（通义千问 DashScope，OpenAI 兼容端点）
    dashscope_api_key: str = ""
    llm_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    llm_model: str = "qwen3.8-max-0902"
    llm_temperature: float = 0.1

    # Embedding（本地 BGE 模型，免费离线）
    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    embedding_device: str = "cpu"
    # HuggingFace 镜像源（国内访问 huggingface.co 需走镜像）
    hf_endpoint: str = "https://hf-mirror.com"

    # 向量库持久化目录
    chroma_persist_dir: str = "./chroma_db"

    # 检索参数
    top_k: int = 8        # 召回数量
    rerank_top_k: int = 4  # 重排后取前几个
    min_relevance_score: float = 0.3  # 相关度阈值：低于此值的片段不参与回答、不作为引用


settings = Settings()

# 让 HuggingFace 库从国内镜像下载模型（解决 huggingface.co 无法直连的问题）
os.environ.setdefault("HF_ENDPOINT", settings.hf_endpoint)
