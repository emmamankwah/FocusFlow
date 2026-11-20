"""Redis-backed sliding-window rate limiting for authentication flows."""

from __future__ import annotations

import hashlib
import os
import secrets
from typing import Iterable

import redis
from redis.exceptions import RedisError


class RateLimitUnavailable(RuntimeError):
    """Raised when Redis cannot enforce an authentication rate limit."""


# Evaluate checks and updates atomically so concurrent API workers share one
# budget. Redis server time keeps workers from disagreeing about timestamps.
_SLIDING_WINDOW_SCRIPT = """
local key = KEYS[1]
local operation = ARGV[1]
local member = ARGV[2]
local rule_count = tonumber(ARGV[3])

local time_parts = redis.call('TIME')
local now = tonumber(time_parts[1]) * 1000 + tonumber(time_parts[2]) / 1000
local longest_window = 0
for i = 1, rule_count do
    local window = tonumber(ARGV[4 + (i - 1) * 2 + 1])
    if window > longest_window then longest_window = window end
end

redis.call('ZREMRANGEBYSCORE', key, '-inf', now - longest_window)
local retry_ms = 0
for i = 1, rule_count do
    local limit = tonumber(ARGV[4 + (i - 1) * 2])
    local window = tonumber(ARGV[4 + (i - 1) * 2 + 1])
    local lower = now - window
    local count = redis.call('ZCOUNT', key, '(' .. lower, '+inf')
    if count >= limit then
        local blocking = redis.call(
            'ZRANGEBYSCORE', key, '(' .. lower, '+inf',
            'WITHSCORES', 'LIMIT', count - limit, 1
        )
        if #blocking >= 2 then
            local wait = tonumber(blocking[2]) + window - now
            if wait > retry_ms then retry_ms = wait end
        end
    end
end

if retry_ms <= 0 and operation == 'hit' then
    redis.call('ZADD', key, now, member)
    redis.call('PEXPIRE', key, longest_window + 1000)
end

return math.ceil(math.max(0, retry_ms))
"""


class RedisSlidingWindowLimiter:
    """Allow at most each configured number of hits in its time window."""

    def __init__(
        self,
        name: str,
        rules: Iterable[tuple[int, int]],
        *,
        redis_url: str | None = None,
    ) -> None:
        self.name = name
        self.rules = tuple(rules)
        if not self.rules:
            raise ValueError("At least one rate limit rule is required.")
        if any(limit < 1 or window <= 0 for limit, window in self.rules):
            raise ValueError("Rate limits must use positive limits and windows.")

        self.client = redis.Redis.from_url(
            redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            socket_connect_timeout=2,
            socket_timeout=2,
            health_check_interval=30,
            decode_responses=True,
        )

    def retry_after(self, key: str) -> float:
        """Return seconds until the key may act again; zero means allowed."""
        return self._run("check", key)

    def hit(self, key: str) -> float:
        """Record a hit, or return the remaining delay when already limited."""
        return self._run("hit", key)

    def _run(self, operation: str, identity: str) -> float:
        digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()
        redis_key = f"focusflow:auth:rate-limit:{self.name}:{digest}"
        args: list[str | int] = [operation, secrets.token_hex(16), len(self.rules)]
        for limit, window_seconds in self.rules:
            args.extend((limit, window_seconds * 1000))

        try:
            retry_ms = self.client.eval(_SLIDING_WINDOW_SCRIPT, 1, redis_key, *args)
        except RedisError as exc:
            raise RateLimitUnavailable(
                "Authentication rate limiting is unavailable."
            ) from exc
        return float(retry_ms) / 1000
