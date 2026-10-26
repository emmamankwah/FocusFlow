"""Thread-safe, in-process sliding-window rate limiting.

The OTP endpoints are synchronous FastAPI handlers, so they run in a worker
thread; the counters are therefore guarded by a lock.

The store lives in memory: restarting the API clears it and
``uvicorn --workers N`` gives every worker its own budget. That is enough to
stop an attacker guessing codes against a single deployment, but move the
counters to Redis (or a shared table) before scaling horizontally.
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
    ) -> None:
        if not rules:
            raise ValueError("At least one rule is required.")
        self.name = name
        self._rules = rules
        self._clock = clock
        self._longest_window = max(window for _, window in rules)
        self._hits: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def retry_after(self, key: str) -> float:
        """Seconds until ``key`` may act again; ``0.0`` means allowed now."""
        with self._lock:
            return self._retry_after_locked(key, self._clock())

    def hit(self, key: str) -> float:
        """Record a hit, or return the seconds to wait when already limited.

        A rejected call is *not* recorded, so repeated attempts cannot push the
        window forward and starve the caller.
        """
        with self._lock:
            now = self._clock()
            wait = self._retry_after_locked(key, now)
            if wait:
                return wait
            self._hits.setdefault(key, deque()).append(now)
            return 0.0

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
