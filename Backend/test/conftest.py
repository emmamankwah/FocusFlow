"""
Shared pytest fixtures for the FocusFlow backend test suite.

The rate-limiter fixture patches every RedisSlidingWindowLimiter instance so
auth tests do not depend on a live Redis connection.

Each limiter stub returns 0 (allowed) by default.  For the email-change send
limiter the stub simulates a cooldown: the first hit per key is free, any
subsequent hit for the same key returns a non-zero wait — matching the
production cooldown behaviour without needing a live Redis connection.
"""
import pytest
from unittest import mock
from collections import defaultdict

import app.authentication.service.auth_service.service_users as _svc

_COOLDOWN_SECONDS = 45   # mirrors OTP_SEND_COOLDOWN_SECONDS


def _make_cooldown_stub():
    """Return a stub whose .hit() enforces a simple per-key cooldown."""
    hit_counts: dict[str, int] = defaultdict(int)

    def _hit(key: str) -> float:
        hit_counts[key] += 1
        if hit_counts[key] > 1:
            return float(_COOLDOWN_SECONDS)   # simulate cooldown wait
        return 0.0

    stub = mock.Mock()
    stub.hit.side_effect = _hit
    stub.retry_after.return_value = 0
    return stub


@pytest.fixture(autouse=True)
def bypass_rate_limiters():
    """Replace all four sliding-window limiters with no-Redis stubs."""
    free_stub = mock.Mock()
    free_stub.hit.return_value = 0
    free_stub.retry_after.return_value = 0

    cooldown_stub = _make_cooldown_stub()

    with (
        mock.patch.object(_svc, "otp_send_limiter",            free_stub),
        mock.patch.object(_svc, "otp_verify_limiter",          free_stub),
        mock.patch.object(_svc, "email_change_send_limiter",   cooldown_stub),
        mock.patch.object(_svc, "email_change_verify_limiter", free_stub),
    ):
        yield
