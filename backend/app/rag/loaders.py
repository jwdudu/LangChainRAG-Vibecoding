"""文档解析：把上传的文件读成 LangChain Document 列表。"""
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    Docx2txtLoader,
)
import openpyxl


def load_file(path: str, filename: str) -> List[Document]:
    """根据扩展名选择对应的解析器。"""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return PyPDFLoader(path).load()
    if ext in (".txt", ".md"):
        return TextLoader(path, encoding="utf-8").load()
    if ext == ".docx":
        return Docx2txtLoader(path).load()
    if ext == ".csv":
        return CSVLoader(path, encoding="utf-8").load()
    if ext in (".xlsx", ".xls"):
        return _load_excel(path)
    raise ValueError(f"不支持的文件类型: {ext}")


def _load_excel(path: str) -> List[Document]:
    """用 openpyxl 把 Excel 每个工作表转成纯文本（单元格用 | 分隔，适合商品表格）。"""
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    docs: List[Document] = []
    for ws in wb.worksheets:
        lines = []
        for row in ws.iter_rows(values_only=True):
            cells = ["" if c is None else str(c) for c in row]
            if any(c.strip() for c in cells):
                lines.append(" | ".join(cells))
        if lines:
            docs.append(Document(page_content="\n".join(lines), metadata={"source": ws.title}))
    wb.close()
    return docs
