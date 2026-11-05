"""Pydantic 参数校验的单元测试（纯校验逻辑）。"""
import pytest
from pydantic import ValidationError
from app.schemas import UserRegister, ChatRequest


class TestUserRegister:
    def test_合法输入通过(self):
        u = UserRegister(username="zhangsan", password="abc123456")
        assert u.username == "zhangsan"

    def test_用户名过短被拒(self):
        with pytest.raises(ValidationError):
            UserRegister(username="a", password="abc123456")

    def test_密码过短被拒(self):
        with pytest.raises(ValidationError):
            UserRegister(username="zhangsan", password="123")


class TestChatRequest:
    def test_合法输入通过(self):
        c = ChatRequest(session_id=1, question="支持退换吗？")
        assert c.session_id == 1

    def test_空问题被拒(self):
        with pytest.raises(ValidationError):
            ChatRequest(session_id=1, question="")
