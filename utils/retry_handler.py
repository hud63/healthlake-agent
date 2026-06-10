"""Exponential-backoff retry decorator for AWS calls.

Skeleton: retries a small set of transient errors. TODO: scope the retryable exceptions to
botocore throttling / 5xx and add jitter + a max elapsed budget.
"""
from __future__ import annotations

import functools
import time
from typing import Any, Callable

MAX_ATTEMPTS = 3
BASE_DELAY_SECONDS = 0.5


def with_retry(fn: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        attempt = 0
        while True:
            try:
                return fn(*args, **kwargs)
            except NotImplementedError:
                raise  # never retry an unimplemented stub
            except Exception:  # TODO: narrow to transient AWS errors
                attempt += 1
                if attempt >= MAX_ATTEMPTS:
                    raise
                time.sleep(BASE_DELAY_SECONDS * (2 ** (attempt - 1)))  # TODO: add jitter

    return wrapper
