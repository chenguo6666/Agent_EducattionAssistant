import os
import unittest
import uuid

from fastapi.testclient import TestClient

os.environ["GEMINI_API_KEY"] = ""
os.environ["LLM_API_KEY"] = ""
os.environ["EMBEDDING_API_KEY"] = ""

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
                    (
                        "工业革命推动了生产力发展，也引发了城市化进程。"
                        "机器生产逐渐取代手工劳动，工厂制度开始形成。"
                        "随着交通和通信改善，商品流通效率提升，"
                        "但也带来了贫富分化和劳动条件恶化等社会问题。"
                    ),
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
        self.assertGreaterEqual(len(summary_payload["agentTrace"]), 3)
        self.assertGreaterEqual(len(summary_payload["toolCalls"]), 1)
        self.assertEqual(summary_payload["toolCalls"][0]["toolName"], "generate_summary_and_quiz")

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
        self.assertEqual(qa_payload["toolCalls"][0]["toolName"], "retrieve_document_chunks")
        self.assertEqual(qa_payload["toolCalls"][1]["toolName"], "answer_with_context")

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

    def test_chat_without_document_returns_direct_assistant_reply(self):
        _, headers = self.create_user_and_login()

        response = self.client.post(
            "/api/chat/execute",
            headers=headers,
            json={"message": "你好，我想准备下周的历史考试，先给我一点复习建议。"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["intent"], "assistant_chat")
        self.assertTrue(payload["result"]["answer"])
        self.assertGreaterEqual(len(payload["agentTrace"]), 2)
        self.assertEqual(payload["toolCalls"], [])

    def test_exam_prediction_phrase_routes_to_quiz(self):
        _, headers = self.create_user_and_login()

        response = self.client.post(
            "/api/chat/execute",
            headers=headers,
            json={"message": "我快考试了，帮我看看可能考哪些题"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["intent"], "quiz")
        self.assertEqual(payload["toolCalls"][0]["toolName"], "generate_quiz")
        self.assertTrue(payload["result"]["quiz"])

    def test_key_points_and_outline_tasks_return_structured_trace(self):
        _, headers = self.create_user_and_login()

        upload_response = self.client.post(
            "/api/documents/upload",
            headers=headers,
            files={
                "file": (
                    "biology.txt",
                    (
                        "细胞膜控制物质进出细胞，细胞核负责遗传信息存储，"
                        "线粒体参与能量转换，核糖体负责蛋白质合成。"
                    ),
                    "text/plain",
                )
            },
        )
        self.assertEqual(upload_response.status_code, 200)
        session_id = upload_response.json()["sessionId"]

        key_points_response = self.client.post(
            "/api/chat/execute",
            headers=headers,
            json={"message": "请提取这份资料的核心知识点", "sessionId": session_id},
        )
        self.assertEqual(key_points_response.status_code, 200)
        key_points_payload = key_points_response.json()
        self.assertEqual(key_points_payload["intent"], "key_points")
        self.assertEqual(key_points_payload["toolCalls"][0]["toolName"], "extract_key_points")
        self.assertTrue(key_points_payload["result"]["answer"])

        outline_response = self.client.post(
            "/api/chat/execute",
            headers=headers,
            json={"message": "请生成这份资料的复习提纲", "sessionId": session_id},
        )
        self.assertEqual(outline_response.status_code, 200)
        outline_payload = outline_response.json()
        self.assertEqual(outline_payload["intent"], "study_outline")
        self.assertEqual(outline_payload["toolCalls"][0]["toolName"], "build_study_outline")
        self.assertTrue(outline_payload["result"]["answer"])

    def test_document_check_task_returns_fast_structured_answer(self):
        _, headers = self.create_user_and_login()

        upload_response = self.client.post(
            "/api/documents/upload",
            headers=headers,
            files={
                "file": (
                    "note.txt",
                    "这是一个很短的测试文件，用来确认系统能否看到当前会话资料。",
                    "text/plain",
                )
            },
        )
        self.assertEqual(upload_response.status_code, 200)
        session_id = upload_response.json()["sessionId"]

        response = self.client.post(
            "/api/chat/execute",
            headers=headers,
            json={"message": "你能看到我刚上传的文件吗", "sessionId": session_id},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["intent"], "document_check")
        self.assertEqual(payload["status"], "completed")
        self.assertEqual(payload["toolCalls"], [])
        self.assertIn("note.txt", payload["result"]["answer"])

    def test_invalid_token_returns_401(self):
        response = self.client.get("/api/auth/me", headers={"Authorization": "Bearer invalid-token"})
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
