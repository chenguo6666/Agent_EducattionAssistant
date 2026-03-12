import os
import unittest
import uuid

from fastapi.testclient import TestClient

os.environ["GEMINI_API_KEY"] = ""

from app.main import app


class AcceptanceTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def create_user_and_login(self):
        suffix = uuid.uuid4().hex[:8]
        username = f"accept_{suffix}"
        phone = f"1{uuid.uuid4().int % 10**10:010d}"
        password = "123456"

        register_response = self.client.post(
            "/api/auth/register",
            json={"username": username, "phone": phone, "password": password},
        )
        self.assertEqual(register_response.status_code, 200)

        login_response = self.client.post(
            "/api/auth/login",
            json={"account": username, "password": password},
        )
        self.assertEqual(login_response.status_code, 200)
        token = login_response.json()["token"]
        return username, {"Authorization": f"Bearer {token}"}

    def test_register_login_and_get_current_user(self):
        username, headers = self.create_user_and_login()
        me_response = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.json()["username"], username)

    def test_login_with_wrong_password_returns_401(self):
        suffix = uuid.uuid4().hex[:8]
        username = f"accept_fail_{suffix}"
        phone = f"1{uuid.uuid4().int % 10**10:010d}"

        self.client.post(
            "/api/auth/register",
            json={"username": username, "phone": phone, "password": "123456"},
        )

        login_response = self.client.post(
            "/api/auth/login",
            json={"account": username, "password": "wrong123"},
        )
        self.assertEqual(login_response.status_code, 401)
        self.assertEqual(login_response.json()["detail"], "账号或密码错误")

    def test_rag_export_and_mistake_workflow(self):
        _, headers = self.create_user_and_login()

        upload_response = self.client.post(
            "/api/documents/upload",
            headers=headers,
            files={
                "file": (
                    "lesson.txt",
                    "工业革命推动了生产力发展，也引发了城市化进程。"
                    "机器生产逐渐取代手工劳动，工厂制度开始形成。"
                    "随着交通和通信改善，商品流通效率提升，但也带来了贫富分化和劳动条件恶化等社会问题。",
                    "text/plain",
                )
            },
        )
        self.assertEqual(upload_response.status_code, 200)
        session_id = upload_response.json()["sessionId"]

        summary_response = self.client.post(
            "/api/chat/execute",
            headers=headers,
            json={
                "message": "请根据当前资料总结重点并生成5个选择题。",
                "sessionId": session_id,
            },
        )
        self.assertEqual(summary_response.status_code, 200)
        summary_payload = summary_response.json()
        self.assertEqual(summary_payload["intent"], "summary_and_quiz")
        self.assertEqual(len(summary_payload["result"]["quiz"]), 5)
        self.assertTrue(summary_payload["recordId"])

        export_response = self.client.get(f"/api/chat/records/{summary_payload['recordId']}/export", headers=headers)
        self.assertEqual(export_response.status_code, 200)
        self.assertIn("教育助手 AI Agent 导出结果", export_response.json()["content"])

        qa_response = self.client.post(
            "/api/chat/execute",
            headers=headers,
            json={
                "message": "它带来了哪些社会问题？",
                "sessionId": session_id,
            },
        )
        self.assertEqual(qa_response.status_code, 200)
        qa_payload = qa_response.json()
        self.assertEqual(qa_payload["intent"], "rag_answer")
        self.assertGreaterEqual(len(qa_payload["retrievedChunks"]), 1)

        attempt_response = self.client.post(
            f"/api/chat/records/{summary_payload['recordId']}/quiz-attempt",
            headers=headers,
            json={
                "answers": [
                    {"questionIndex": 0, "userAnswer": "B"},
                    {"questionIndex": 1, "userAnswer": "B"},
                    {"questionIndex": 2, "userAnswer": "B"},
                    {"questionIndex": 3, "userAnswer": "B"},
                    {"questionIndex": 4, "userAnswer": "B"},
                ]
            },
        )
        self.assertEqual(attempt_response.status_code, 200)
        self.assertGreaterEqual(attempt_response.json()["savedMistakes"], 1)

        mistakes_response = self.client.get("/api/chat/mistakes", headers=headers)
        self.assertEqual(mistakes_response.status_code, 200)
        self.assertGreaterEqual(len(mistakes_response.json()["items"]), 1)

    def test_invalid_token_returns_401(self):
        response = self.client.get("/api/auth/me", headers={"Authorization": "Bearer invalid-token"})
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
