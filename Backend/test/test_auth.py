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
        self.sent_notices: list[dict] = []

        self._send_patch = mock.patch.object(
            service_users,
            "send_verification_email",
            side_effect=self._capture_email,
        )
        self._send_patch.start()
        self.addCleanup(self._send_patch.stop)

        self._change_send_patch = mock.patch.object(
            service_users,
            "send_email_change_verification",
            side_effect=self._capture_email,
        )
        self._change_send_patch.start()
        self.addCleanup(self._change_send_patch.stop)

        self._notice_patch = mock.patch.object(
            service_users,
            "send_email_change_notice",
            side_effect=self._capture_notice,
        )
        self._notice_patch.start()
        self.addCleanup(self._notice_patch.stop)

        self.addCleanup(self._cleanup)

    def _capture_email(self, user_email, plain_otp, expires_minutes):
        self.sent_otps.append({"email": user_email, "otp": plain_otp})

    def _capture_notice(self, old_email, new_email):
        self.sent_notices.append({"old_email": old_email, "new_email": new_email})

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
                    "DELETE FROM pending_email_changes "
                    "WHERE new_email = ANY(%s) OR user_id IN "
                    "(SELECT id FROM users WHERE email = ANY(%s))",
                    (self.emails, self.emails),
                )
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

    def _headers(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}

    def _request_email_change(
        self,
        headers: dict,
        new_email: str,
        password: str = PASSWORD,
    ):
        return self.client.post(
            "/auth/profile/email",
            headers=headers,
            json={"newEmail": new_email, "currentPassword": password},
        )

    def _verify_email_change(self, headers: dict, otp: str):
        return self.client.post(
            "/auth/profile/email/verify",
            headers=headers,
            json={"otp": otp},
        )

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
        headers = self._headers(login["access_token"])

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
            },
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["username"], new_username)

        changed = self.client.post(
            "/auth/change-password",
            headers=headers,
            json={
                "oldPassword": PASSWORD,
                "newPassword": NEW_PASSWORD,
            },
        )
        self.assertEqual(changed.status_code, 200)
        self.assertNotIn("error", changed.json())
        self.assertIn("access_token", changed.json())

        self.assertEqual(
            self.client.get("/auth/profile", headers=headers).status_code,
            401,
        )
        new_headers = self._headers(changed.json()["access_token"])
        self.assertEqual(
            self.client.get("/auth/profile", headers=new_headers).status_code,
            200,
        )

        self.assertIn("error", self._login(email, PASSWORD))
        self.assertIn("access_token", self._login(email, NEW_PASSWORD))

    def test_profile_rejects_email_field(self):
        email, username = self._verified_user()
        token = self._login(email)["access_token"]
        headers = self._headers(token)

        updated = self.client.put(
            "/auth/profile",
            headers=headers,
            json={
                "firstName": "Ada",
                "lastName": "Lovelace",
                "username": username,
                "email": _email(),
            },
        )
        self.assertEqual(updated.status_code, 422)
        self.assertEqual(
            self.client.get("/auth/profile", headers=headers).json()["email"],
            email,
        )

        changed = self.client.post(
            "/auth/change-password",
            headers=headers,
            json={
                "email": email,
                "oldPassword": PASSWORD,
                "newPassword": NEW_PASSWORD,
            },
        )
        self.assertEqual(changed.status_code, 422)

    def test_password_change_invalidates_existing_tokens(self):
        email, _ = self._verified_user()
        token = self._login(email)["access_token"]
        headers = self._headers(token)

        changed = self.client.post(
            "/auth/change-password",
            headers=headers,
            json={"oldPassword": PASSWORD, "newPassword": NEW_PASSWORD},
        )
        self.assertNotIn("error", changed.json())

        self.assertEqual(
            self.client.get("/auth/profile", headers=headers).status_code,
            401,
        )
        new_headers = self._headers(changed.json()["access_token"])
        self.assertEqual(
            self.client.get("/auth/profile", headers=new_headers).status_code,
            200,
        )

    def test_password_reset_invalidates_existing_tokens(self):
        email = _email()
        username = _username()
        self.emails.append(email)
        create_user("Reset", "User", email, username, hash_password(PASSWORD))
        token = self._login(email)["access_token"]
        headers = self._headers(token)

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

        self.assertEqual(
            self.client.get("/auth/profile", headers=headers).status_code,
            401,
        )
        self.assertIn("access_token", self._login(email, NEW_PASSWORD))
        self.assertIn("error", self._login(email, PASSWORD))

    def test_email_change_requires_current_password(self):
        email, _ = self._verified_user()
        token = self._login(email)["access_token"]
        headers = self._headers(token)

        new_email = _email()
        self.emails.append(new_email)
        response = self._request_email_change(headers, new_email, "Wrong!Pass1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json().get("error"),
            "Current password is incorrect.",
        )
        self.assertFalse(
            any(item["email"] == new_email for item in self.sent_otps)
        )
        self.assertEqual(
            self.client.get("/auth/profile", headers=headers).json()["email"],
            email,
        )

    def test_email_change_flow_updates_identity_and_invalidates_tokens(self):
        old_email, _ = self._verified_user()
        token = self._login(old_email)["access_token"]
        headers = self._headers(token)

        new_email = _email()
        self.emails.append(new_email)

        requested = self._request_email_change(headers, new_email)
        self.assertEqual(requested.status_code, 200)
        self.assertNotIn("error", requested.json())
        self.assertEqual(
            self.client.get("/auth/profile", headers=headers).json()["email"],
            old_email,
        )
        self.assertIn("error", self._login(new_email))

        otp = self._otp(new_email)
        wrong = "000000" if otp != "000000" else "111111"
        rejected = self._verify_email_change(headers, wrong)
        self.assertIn("Invalid code", rejected.json()["error"])

        verified = self._verify_email_change(headers, otp)
        self.assertEqual(verified.status_code, 200)
        self.assertNotIn("error", verified.json())
        self.assertEqual(verified.json()["email"], new_email)
        self.assertIn("access_token", verified.json())

        self.assertEqual(
            self.sent_notices,
            [{"old_email": old_email, "new_email": new_email}],
        )
        self.assertEqual(
            self.client.get("/auth/profile", headers=headers).status_code,
            401,
        )
        new_headers = self._headers(verified.json()["access_token"])
        self.assertEqual(
            self.client.get("/auth/profile", headers=new_headers).json()["email"],
            new_email,
        )
        self.assertIn("error", self._login(old_email))
        self.assertIn("access_token", self._login(new_email))

    def test_email_change_rejects_same_and_duplicate_emails(self):
        email, _ = self._verified_user()
        token = self._login(email)["access_token"]
        headers = self._headers(token)

        same = self._request_email_change(headers, email)
        self.assertEqual(
            same.json().get("error"),
            "New email must be different from the current email.",
        )

        other_email, _ = self._verified_user()
        duplicate = self._request_email_change(headers, other_email)
        self.assertEqual(duplicate.json().get("error"), "Email already in use.")

        pending_email, _, pending = self._register()
        self.assertNotIn("error", pending.json())
        pending_response = self._request_email_change(headers, pending_email)
        self.assertEqual(
            pending_response.json().get("error"),
            "Email already in use.",
        )

        second_email, _ = self._verified_user()
        second_headers = self._headers(self._login(second_email)["access_token"])
        target = _email()
        self.emails.append(target)
        first_request = self._request_email_change(headers, target)
        self.assertNotIn("error", first_request.json())

        second_request = self._request_email_change(second_headers, target)
        self.assertEqual(
            second_request.json().get("error"),
            "Email already in use.",
        )

    def test_email_change_resend_cooldown(self):
        email, _ = self._verified_user()
        headers = self._headers(self._login(email)["access_token"])

        new_email = _email()
        self.emails.append(new_email)

        first = self._request_email_change(headers, new_email)
        self.assertNotIn("error", first.json())

        second = self._request_email_change(headers, new_email)
        self.assertIn("Too many verification emails requested", second.json()["error"])

    def test_email_change_cancel_discards_pending_code(self):
        email, _ = self._verified_user()
        headers = self._headers(self._login(email)["access_token"])

        new_email = _email()
        self.emails.append(new_email)
        requested = self._request_email_change(headers, new_email)
        self.assertNotIn("error", requested.json())

        cancelled = self.client.delete("/auth/profile/email", headers=headers)
        self.assertEqual(cancelled.status_code, 200)
        self.assertNotIn("error", cancelled.json())

        verified = self._verify_email_change(headers, self._otp(new_email))
        self.assertEqual(
            verified.json().get("error"),
            "No active email change. Request a new one.",
        )

    def test_email_change_expired_code_is_rejected(self):
        email, _ = self._verified_user()
        headers = self._headers(self._login(email)["access_token"])

        new_email = _email()
        self.emails.append(new_email)
        requested = self._request_email_change(headers, new_email)
        self.assertNotIn("error", requested.json())

        connection = database_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE pending_email_changes "
                    "SET expires_at = now() - interval '1 minute' "
                    "WHERE new_email = %s",
                    (new_email,),
                )
            connection.commit()
        finally:
            connection.close()

        verified = self._verify_email_change(headers, self._otp(new_email))
        self.assertIn("expired", verified.json()["error"].lower())

    def test_email_change_preserves_case_and_trims_whitespace(self):
        base = f"AuthFlow+{uuid.uuid4().hex}"
        email = f"{base}@Example.COM"
        lower_email = email.lower()
        padded = f"  {email}  "
        self.emails.extend([email, lower_email])

        registered = self.client.post(
            "/auth/register",
            json=_payload(padded, _username()),
        )
        self.assertEqual(registered.status_code, 200)
        self.assertNotIn("error", registered.json())

        verified = self.client.post(
            "/auth/verify-otp",
            json={"email": email, "otp": self._otp(email)},
        )
        self.assertNotIn("error", verified.json())

        login = self._login(email)
        self.assertIn("access_token", login)
        headers = self._headers(login["access_token"])
        self.assertEqual(
            self.client.get("/auth/profile", headers=headers).json()["email"],
            email,
        )
        self.assertIn("error", self._login(lower_email))

        changed = self._request_email_change(headers, lower_email)
        self.assertNotIn("error", changed.json())
        verified_change = self._verify_email_change(
            headers,
            self._otp(lower_email),
        )
        self.assertNotIn("error", verified_change.json())
        self.assertEqual(verified_change.json()["email"], lower_email)
        self.assertIn("access_token", self._login(lower_email))
        self.assertIn("error", self._login(email))

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


if __name__ == "__main__":
    unittest.main()
