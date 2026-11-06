"""
Locust 压测脚本：模拟 100 个在线用户使用电商知识库问答系统。

用法（headless，命令行跑）：
  cd backend
  .venv/Scripts/python.exe -m locust -f locustfile.py --host http://127.0.0.1:8000 \
      --headless --users 100 --spawn-rate 5 --run-time 2m --html report.html

参数说明：
  --users 100     在线用户总数（虚拟用户）
  --spawn-rate 5  每秒增加 5 个用户（慢慢爬坡，避免瞬间打崩）
  --run-time 2m   跑 2 分钟
  --html 报告.html 生成 HTML 报告
"""
import random
from locust import HttpUser, task, between

# 预注册的测试账号（用户名，密码统一 test123456）
USERNAMES = [f"loadtest{i:02d}" for i in range(1, 51)]
PASSWORD = "test123456"

# 与知识库相关的问题（让检索能命中内容）
QUESTIONS = [
    "帮我推荐一个尺码",
    "这款耳机支持退换吗？",
    "手表续航多久？",
    "这款商品有什么特点？",
]


class RAGUser(HttpUser):
    # 用户思考停顿 2~6 秒（模拟读回答、打字）
    wait_time = between(2, 6)

    def on_start(self):
        """每个虚拟用户启动时登录一次，拿 token。"""
        username = random.choice(USERNAMES)
        with self.client.post(
            "/api/auth/login",
            json={"username": username, "password": PASSWORD},
            name="POST /api/auth/login",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                self.token = resp.json()["access_token"]
                self.headers = {"Authorization": f"Bearer {self.token}"}
            else:
                self.token = None
                resp.failure(f"登录失败 HTTP {resp.status_code}")

    @task(6)
    def list_sessions(self):
        """轻量：看会话列表。"""
        if not getattr(self, "token", None):
            return
        self.client.get("/api/sessions", headers=self.headers, name="GET /api/sessions")

    @task(2)
    def create_session(self):
        """中量：新建会话。"""
        if not getattr(self, "token", None):
            return
        self.client.post("/api/sessions", json={"title": "压测会话"}, headers=self.headers, name="POST /api/sessions")

    @task(1)
    def chat(self):
        """重量：RAG 问答（向量检索 + LLM 流式）。"""
        if not getattr(self, "token", None):
            return
        # 先建一个会话
        r = self.client.post(
            "/api/sessions", json={"title": "压测"}, headers=self.headers, name="POST /api/sessions"
        )
        if r.status_code != 200:
            return
        sid = r.json()["id"]
        # 发问（SSE 流式会完整返回，Locust 记录完整耗时）
        self.client.post(
            "/api/chat",
            json={"session_id": sid, "question": random.choice(QUESTIONS)},
            headers=self.headers,
            name="POST /api/chat (RAG)",
            timeout=120,
        )
