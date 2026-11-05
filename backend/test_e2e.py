"""端到端测试脚本：登录 → 建会话 → 流式问答 → 验证引用来源。"""
import httpx

BASE = "http://127.0.0.1:8000"


def main():
    with httpx.Client(base_url=BASE, timeout=180) as c:
        # 1. 登录
        r = c.post("/api/auth/login", json={"username": "testuser", "password": "abc123456"})
        r.raise_for_status()
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("1. 登录成功:", r.json()["user"])

        # 2. 创建会话
        r = c.post("/api/sessions", json={"title": "新会话"}, headers=headers)
        r.raise_for_status()
        sid = r.json()["id"]
        print("2. 创建会话:", r.json())

        # 3. 流式问答
        question = "这款无线蓝牙耳机支持退换吗？"
        print("3. 提问:", question)
        with c.stream("POST", "/api/chat", json={"session_id": sid, "question": question}, headers=headers) as resp:
            print("   状态码:", resp.status_code)
            for line in resp.iter_lines():
                if line:
                    print(line)

        # 4. 校验历史消息已持久化
        r = c.get(f"/api/sessions/{sid}/messages", headers=headers)
        msgs = r.json()
        print("4. 历史消息条数:", len(msgs))
        for m in msgs:
            print(f"   [{m['role']}] {m['content'][:60]}... 来源数={len(m['sources'] or [])}")


if __name__ == "__main__":
    main()
