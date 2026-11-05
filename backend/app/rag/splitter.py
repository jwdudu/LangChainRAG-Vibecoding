"""文本分块。"""
from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_splitter() -> RecursiveCharacterTextSplitter:
    """中文感知的递归分块：优先按段落/换行/句号等边界切分，带重叠避免语义断裂。"""
    return RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
    )
