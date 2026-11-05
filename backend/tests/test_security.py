"""密码哈希 与 JWT 令牌 的单元测试（纯逻辑，不碰数据库/网络）。"""
from app.core.security import hash_password, verify_password, create_access_token, decode_token


class TestPassword:
    def test_hash_不同于明文(self):
        """哈希结果不能等于明文，数据库不存明文密码。"""
        hashed = hash_password("abc123456")
        assert hashed != "abc123456"

    def test_正确密码校验通过(self):
        hashed = hash_password("abc123456")
        assert verify_password("abc123456", hashed) is True

    def test_错误密码校验失败(self):
        hashed = hash_password("abc123456")
        assert verify_password("wrong-password", hashed) is False

    def test_加盐后两次哈希不同(self):
        """同一密码两次哈希结果应不同（bcrypt 加盐）。"""
        assert hash_password("abc123456") != hash_password("abc123456")

    def test_中文密码(self):
        hashed = hash_password("密码123456")
        assert verify_password("密码123456", hashed) is True


class TestJwt:
    def test_签发后能正确解析(self):
        token = create_access_token("testuser")
        assert decode_token(token) == "testuser"

    def test_非法令牌返回None(self):
        assert decode_token("not-a-valid-token") is None

    def test_篡改令牌返回None(self):
        token = create_access_token("testuser")
        assert decode_token(token + "x") is None
