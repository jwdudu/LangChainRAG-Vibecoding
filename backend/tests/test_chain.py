"""RAG 生成链 build_context 的单元测试（纯字符串拼接，不调大模型）。"""
from app.rag.chain import build_context


class _Doc:
    """模拟一个带 page_content 的文档对象。"""
    def __init__(self, content):
        self.page_content = content


class TestBuildContext:
    def test_每个片段带编号(self):
        docs = [_Doc("第一段"), _Doc("第二段"), _Doc("第三段")]
        ctx = build_context(docs)
        assert "[1] 第一段" in ctx
        assert "[2] 第二段" in ctx
        assert "[3] 第三段" in ctx

    def test_空列表返回空字符串(self):
        assert build_context([]) == ""

    def test_片段用空行分隔(self):
        docs = [_Doc("A"), _Doc("B")]
        assert build_context(docs) == "[1] A\n\n[2] B"
