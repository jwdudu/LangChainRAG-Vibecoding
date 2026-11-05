"""文本分块的单元测试（langchain 分块器，纯 CPU 计算，不加载模型）。"""
from app.rag.splitter import get_splitter


class TestSplitter:
    def test_长文本被切分(self):
        splitter = get_splitter()
        text = "这是第一句话。" * 200  # 约 1200 字，超过 chunk_size=500
        chunks = splitter.split_text(text)
        assert len(chunks) > 1

    def test_短文本不分块(self):
        splitter = get_splitter()
        chunks = splitter.split_text("短文本")
        assert len(chunks) == 1
        assert chunks[0] == "短文本"
