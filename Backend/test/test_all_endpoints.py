import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from main import app


class EndpointMatrixTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    # 1. System Health & Info
    def test_root_endpoint(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("message", res.json())
        self.assertEqual(res.json()["message"], "FocusFlow API is running")

    def test_health_endpoint(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"status": "ok"})

    # 2. AI Subsystem
    def test_ai_health_endpoint(self):
        res = self.client.get("/ai/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"status": "ok"})

    def test_ai_chat_requires_auth(self):
        res = self.client.post("/ai/chat", json={})
        self.assertEqual(res.status_code, 401)

    def test_planner_generate_endpoint(self):
        payload = {
            "tasks": [
                {"id": 1, "title": "Implement matrix test", "deadline": None, "priority": 1},
                {"id": 2, "title": "Run all tests", "deadline": None, "priority": 2},
            ]
        }
        res = self.client.post("/ai/planner/generate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("tasks", data)
        self.assertEqual(len(data["tasks"]), 2)
        self.assertIn("scheduled_time", data["tasks"][0])

    # 3. Documents & RAG Security Checks (Unauthenticated requests must be rejected)
    def test_get_documents_requires_auth(self):
        res = self.client.get("/ai/documents")
        self.assertEqual(res.status_code, 401)

    def test_post_document_text_requires_auth(self):
        res = self.client.post("/ai/documents/text", json={"title": "Test", "content": "Sample"})
        self.assertEqual(res.status_code, 401)

    def test_rag_query_requires_auth(self):
        res = self.client.post("/ai/rag/query", json={"question": "What is FocusFlow?"})
        self.assertEqual(res.status_code, 401)

    # 4. Authentication Endpoints Validation & Rejection of Bad Inputs
    def test_auth_register_validation(self):
        res = self.client.post("/auth/register", json={"email": "not-an-email"})
        self.assertEqual(res.status_code, 422)

    def test_auth_login_invalid_credentials(self):
        res = self.client.post(
            "/auth/login",
            json={"email": "nonexistent_user_9999@example.com", "password": "WrongPassword!123"},
        )
        self.assertEqual(res.status_code, 401)
        self.assertIn("error", res.json())

    def test_auth_profile_requires_auth(self):
        res = self.client.get("/auth/profile")
        self.assertEqual(res.status_code, 401)

    def test_auth_update_profile_requires_auth(self):
        res = self.client.put("/auth/profile", json={"username": "newname"})
        self.assertEqual(res.status_code, 401)

    def test_auth_profile_email_change_requires_auth(self):
        res = self.client.post("/auth/profile/email", json={"newEmail": "new@example.com", "currentPassword": "pw"})
        self.assertEqual(res.status_code, 401)

    def test_auth_profile_email_verify_requires_auth(self):
        res = self.client.post("/auth/profile/email/verify", json={"otp": "123456"})
        self.assertEqual(res.status_code, 401)

    def test_auth_profile_email_cancel_requires_auth(self):
        res = self.client.delete("/auth/profile/email")
        self.assertEqual(res.status_code, 401)

    def test_auth_change_password_requires_auth(self):
        res = self.client.post(
            "/auth/change-password",
            json={"oldPassword": "old", "newPassword": "new"},
        )
        self.assertEqual(res.status_code, 401)


if __name__ == "__main__":
    unittest.main()
