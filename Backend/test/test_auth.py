import sys
import unittest
import uuid
from pathlib import Path
from unittest import mock

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient

from app.authentication.repository.authentication.user_repo import create_user
from app.authentication.security.secure_users import hash_password
from app.authentication.service.auth_service import service_users
from app.authentication.settings.db import database_connection
from main import app

PASSWORD = "Str0ng!Passw0rd"
NEW_PASSWORD = "N3w!Passw0rd"


def _email() -> str:
    return f"authflow+{uuid.uuid4().hex}@example.com"


def _username() -> str:
    return f"au{uuid.uuid4().hex[:12]}"


def _payload(email: str, username: str, password: str = PASSWORD) -> dict:
    return {
        "firstName": "Ada",
        "lastName": "Lovelace",
        "email": email,
        "username": username,
        "password": password,
        "confirmPassword": password,
    }


class AuthFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        connection = database_connection()
        if connection is None:
            raise unittest.SkipTest("PostgreSQL is not available")
        connection.close()

    def setUp(self):
        self.client = TestClient(app)
        self.emails: list[str] = []
        self.sent_otps: list[dict] = []
        self._send_patch = mock.patch.object(
            service_users,
            "send_verification_email",
            side_effect=self._capture_email,
        )
        self._send_patch.start()
        self.addCleanup(self._send_patch.stop)
        self.addCleanup(self._cleanup)

    def _capture_email(self, user_email, plain_otp, expires_minutes):
        self.sent_otps.append({"email": user_email, "otp": plain_otp})

    def _otp(self, email: str) -> str:
        for item in reversed(self.sent_otps):
            if item["email"] == email:
                return item["otp"]
        self.fail(f"No verification code was captured for {email}")

    def _cleanup(self):
        connection = database_connection()
        if connection is None or not self.emails:
            return
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM otp_table WHERE email = ANY(%s)",
                    (self.emails,),
                )
                cursor.execute(
                    "DELETE FROM pending_users WHERE email = ANY(%s)",
                    (self.emails,),
                )
                cursor.execute(
                    "DELETE FROM users WHERE email = ANY(%s)",
                    (self.emails,),
                )
            connection.commit()
        finally:
            connection.close()

    def _register(
        self,
        email: str | None = None,
        username: str | None = None,
        password: str = PASSWORD,
    ):
        email = email or _email()
        username = username or _username()
        self.emails.append(email)
        response = self.client.post(
            "/auth/register",
            json=_payload(email, username, password),
        )
        return email, username, response

    def _verified_user(self):
        email, username, response = self._register()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("error", response.json())

        verify = self.client.post(
            "/auth/verify-otp",
            json={"email": email, "otp": self._otp(email)},
        )
        self.assertEqual(verify.status_code, 200)
        self.assertNotIn("error", verify.json())
        return email, username

    def _login(self, email: str, password: str = PASSWORD) -> dict:
        response = self.client.post(
            "/auth/login",
            json={"email": email, "password": password},
        )
        return response.json()

    def test_register_verify_login_profile_and_change_password(self):
        email, username, response = self._register()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["message"],
            "Verification code sent. Check your email.",
        )

        verify = self.client.post(
            "/auth/verify-otp",
            json={"email": email, "otp": self._otp(email)},
        )
        self.assertEqual(verify.status_code, 200)
        self.assertEqual(
            verify.json()["message"],
            "Email verified. You can now log in.",
        )

        login = self._login(email)
        self.assertIn("access_token", login)
        headers = {"Authorization": f"Bearer {login['access_token']}"}

        profile = self.client.get("/auth/profile", headers=headers)
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(profile.json()["email"], email)
        self.assertEqual(profile.json()["username"], username)

        new_username = _username()
        updated = self.client.put(
            "/auth/profile",
            headers=headers,
            json={
                "firstName": "Ada",
                "lastName": "Lovelace",
                "username": new_username,
                "email": email,
            },
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["username"], new_username)

        changed = self.client.post(
            "/auth/change-password",
            headers=headers,
            json={
                "email": email,
                "oldPassword": PASSWORD,
                "newPassword": NEW_PASSWORD,
            },
        )
        self.assertEqual(changed.status_code, 200)
        self.assertNotIn("error", changed.json())

        self.assertIn("error", self._login(email, PASSWORD))
        self.assertIn("access_token", self._login(email, NEW_PASSWORD))

    def test_password_reset_flow(self):
        email = _email()
        username = _username()
        self.emails.append(email)
        create_user("Reset", "User", email, username, hash_password(PASSWORD))

        requested = self.client.post(
            "/auth/forgot-password",
            json={"email": email},
        )
        self.assertEqual(requested.status_code, 200)
        self.assertNotIn("error", requested.json())

        otp = self._otp(email)
        verified = self.client.post(
            "/auth/verify-reset-otp",
            json={"email": email, "otp": otp},
        )
        self.assertEqual(verified.status_code, 200)
        self.assertNotIn("error", verified.json())

        reset = self.client.post(
            "/auth/reset-password",
            json={"email": email, "otp": otp, "newPassword": NEW_PASSWORD},
        )
        self.assertEqual(reset.status_code, 200)
        self.assertNotIn("error", reset.json())

        self.assertIn("access_token", self._login(email, NEW_PASSWORD))
        self.assertIn("error", self._login(email, PASSWORD))

    def test_wrong_otp_is_rejected_then_correct_otp_works(self):
        email, _, _ = self._register()
        otp = self._otp(email)
        wrong = "000000" if otp != "000000" else "111111"

        rejected = self.client.post(
            "/auth/verify-otp",
            json={"email": email, "otp": wrong},
        )
        self.assertEqual(rejected.status_code, 200)
        self.assertIn("Invalid code", rejected.json()["error"])

        accepted = self.client.post(
            "/auth/verify-otp",
            json={"email": email, "otp": otp},
        )
        self.assertEqual(accepted.status_code, 200)
        self.assertNotIn("error", accepted.json())

    def test_duplicate_email_and_username_are_rejected(self):
        email, username = self._verified_user()

        other_email = _email()
        self.emails.append(other_email)
        duplicate_email = self.client.post(
            "/auth/register",
            json=_payload(email, _username()),
        )
        self.assertIn("error", duplicate_email.json())
        self.assertEqual(
            duplicate_email.json()["error"],
            "Email already registered.",
        )

        duplicate_username = self.client.post(
            "/auth/register",
            json=_payload(other_email, username),
        )
        self.assertIn("error", duplicate_username.json())
        self.assertEqual(
            duplicate_username.json()["error"],
            "Username already taken.",
        )

    def test_profile_email_change_updates_login_identity(self):
        old_email, username = self._verified_user()
        token = self._login(old_email)["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        new_email = _email()
        self.emails.append(new_email)

        updated = self.client.put(
            "/auth/profile",
            headers=headers,
            json={
                "firstName": "Ada",
                "lastName": "Lovelace",
                "username": username,
                "email": new_email,
            },
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["email"], new_email)

        profile = self.client.get("/auth/profile", headers=headers)
        self.assertEqual(profile.json()["email"], new_email)

        self.assertIn("access_token", self._login(new_email, PASSWORD))
        self.assertIn("error", self._login(old_email, PASSWORD))
        self.assertFalse(
            any(item["email"] == new_email for item in self.sent_otps)
        )

    def test_profile_email_change_rejects_registered_email(self):
        email, username = self._verified_user()
        token = self._login(email)["access_token"]

        other_email = _email()
        other_username = _username()
        self.emails.append(other_email)
        create_user(
            "Other",
            "User",
            other_email,
            other_username,
            hash_password(PASSWORD),
        )

        response = self.client.put(
            "/auth/profile",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "firstName": "Ada",
                "lastName": "Lovelace",
                "username": username,
                "email": other_email,
            },
        )
        self.assertEqual(response.json().get("error"), "Email already in use.")

    def test_profile_email_change_rejects_pending_email(self):
        email, username = self._verified_user()
        token = self._login(email)["access_token"]

        pending_email, _, pending = self._register()
        self.assertNotIn("error", pending.json())

        response = self.client.put(
            "/auth/profile",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "firstName": "Ada",
                "lastName": "Lovelace",
                "username": username,
                "email": pending_email,
            },
        )
        self.assertEqual(response.json().get("error"), "Email already in use.")

    @unittest.expectedFailure
    def test_register_rejects_username_held_by_pending_registration(self):
        _, username, first = self._register()
        self.assertEqual(first.status_code, 200)

        second_email = _email()
        self.emails.append(second_email)
        second = self.client.post(
            "/auth/register",
            json=_payload(second_email, username),
        )
        self.assertEqual(second.status_code, 200)
        self.assertEqual(
            second.json().get("error"),
            "Username already taken.",
        )

    def test_register_rejects_whitespace_in_username(self):
        for username in ("   ", "ada lovelace", "ada\tlovelace"):
            _, _, response = self._register(username=username)
            self.assertEqual(response.status_code, 422)
            self.assertIn("detail", response.json())

    @unittest.expectedFailure
    def test_profile_email_change_requires_verification(self):
        email, _ = self._verified_user()
        token = self._login(email)["access_token"]

        new_email = _email()
        self.emails.append(new_email)
        response = self.client.put(
            "/auth/profile",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "firstName": "Ada",
                "lastName": "Lovelace",
                "username": _username(),
                "email": new_email,
            },
        )
        self.assertIn("verification", response.json().get("message", "").lower())

    @unittest.expectedFailure
    def test_password_change_invalidates_existing_tokens(self):
        email, _ = self._verified_user()
        token = self._login(email)["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        changed = self.client.post(
            "/auth/change-password",
            headers=headers,
            json={
                "email": email,
                "oldPassword": PASSWORD,
                "newPassword": NEW_PASSWORD,
            },
        )
        self.assertNotIn("error", changed.json())

        profile = self.client.get("/auth/profile", headers=headers)
        self.assertEqual(profile.status_code, 401)


if __name__ == "__main__":
    unittest.main()
