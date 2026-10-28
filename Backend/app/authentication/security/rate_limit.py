"""Thread-safe, in-process sliding-window rate limiting.

The OTP endpoints are synchronous FastAPI handlers, so they run in a worker
thread; the counters are therefore guarded by a lock.

The store lives in memory: restarting the API clears it and
``uvicorn --workers N`` gives every worker its own budget. That is enough to
stop an attacker guessing codes against a single deployment, but move the
counters to Redis (or a shared table) before scaling horizontally.

Keys are evicted once their hits expire, and the store is capped at
``max_keys`` so traffic to fresh addresses cannot grow it without bound. An
evicted key simply starts with a fresh budget.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from typing import Callable

Rule = tuple[int, int]  # (max hits, window in seconds)


class SlidingWindowLimiter:
    """Allow at most ``limit`` hits per key inside each configured window."""

    def __init__(
        self,
        name: str,
        rules: tuple[Rule, ...],
        clock: Callable[[], float] = time.monotonic,
        *,
        max_keys: int = 10_000,
        sweep_interval: float = 60.0,
    ) -> None:
        if not rules:
            raise ValueError("At least one rule is required.")
        if any(
            not isinstance(limit, int)
            or not isinstance(window, (int, float))
            or limit < 1
            or window <= 0
            for limit, window in rules
        ):
            raise ValueError("Rules must use positive numeric limits and windows.")
        if max_keys < 1:
            raise ValueError("max_keys must be at least 1.")
        if sweep_interval <= 0:
            raise ValueError("sweep_interval must be positive.")

        self.name = name
        self._rules = rules
        self._clock = clock
        self._longest_window = max(window for _, window in rules)
        self._max_keys = max_keys
        self._sweep_interval = sweep_interval
        self._hits: dict[str, deque[float]] = {}
        self._last_sweep = clock()
        self._lock = threading.Lock()

    def retry_after(self, key: str) -> float:
        """Seconds until ``key`` may act again; ``0.0`` means allowed now."""
        with self._lock:
            now = self._clock()
            self._maybe_evict(now)
            return self._retry_after_locked(key, now)

    def hit(self, key: str) -> float:
        """Record a hit, or return the seconds to wait when already limited.

        A rejected call is *not* recorded, so repeated attempts cannot push the
        window forward and starve the caller.
        """
        with self._lock:
            now = self._clock()
            self._maybe_evict(now)
            wait = self._retry_after_locked(key, now)
            if wait:
                return wait
            if key not in self._hits:
                self._make_room()
            self._hits.setdefault(key, deque()).append(now)
            return 0.0

    def _make_room(self) -> None:
        """Keep the store at or below ``max_keys`` before inserting a new key."""
        while len(self._hits) >= self._max_keys:
            del self._hits[next(iter(self._hits))]

    def _maybe_evict(self, now: float) -> None:
        if (
            now - self._last_sweep < self._sweep_interval
            and len(self._hits) <= self._max_keys
        ):
            return

        cutoff = now - self._longest_window
        for key in list(self._hits):
            hits = self._hits[key]
            while hits and hits[0] <= cutoff:
                hits.popleft()
            if not hits:
                del self._hits[key]

        # A burst of unique keys can outpace expiry. Drop the oldest keys to
        # keep memory bounded; they get a fresh budget if they come back.
        while len(self._hits) > self._max_keys:
            del self._hits[next(iter(self._hits))]

        self._last_sweep = now

    def _retry_after_locked(self, key: str, now: float) -> float:
        hits = self._hits.get(key)
        if not hits:
            return 0.0

        # Discard entries that no rule can see any more.
        cutoff = now - self._longest_window
        while hits and hits[0] <= cutoff:
            hits.popleft()
        if not hits:
            del self._hits[key]
            return 0.0

        wait = 0.0
        for limit, window in self._rules:
            inside = [stamp for stamp in hits if now - stamp < window]
            if len(inside) >= limit:
                # The key frees up once the oldest blocking hit leaves.
                blocking = inside[-limit]
                wait = max(wait, window - (now - blocking))
        return wait
