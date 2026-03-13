import unittest
import uuid

from fastapi.testclient import TestClient

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

    def test_chat_execute_summary_and_quiz(self):
        _, headers = self.create_user_and_login()
        chat_response = self.client.post(
            "/api/chat/execute",
            headers=headers,
            json={"message": "总结这段历史材料并生成5个选择题：工业革命改变了社会结构。"},
        )

        self.assertEqual(chat_response.status_code, 200)
        payload = chat_response.json()
        self.assertEqual(payload["intent"], "summary_and_quiz")
        self.assertEqual(payload["status"], "completed")
        self.assertEqual(len(payload["timeline"]), 4)
        self.assertEqual(len(payload["result"]["quiz"]), 5)

    def test_invalid_token_returns_401(self):
        response = self.client.get("/api/auth/me", headers={"Authorization": "Bearer invalid-token"})
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
