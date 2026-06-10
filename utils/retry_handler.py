"""Exponential-backoff retry decorator for AWS calls.

Retries transient throttling and 5xx responses with growing delay and jitter, up to a small attempt
budget. Client errors that are not transient are raised immediately.
"""
from __future__ import annotations

import functools
import random
import time
from typing import Any, Callable

from botocore.exceptions import ClientError

MAX_ATTEMPTS = 3
BASE_DELAY_SECONDS = 0.5
_RETRYABLE = {"ThrottlingException", "TooManyRequestsException", "ServiceUnavailable",
              "InternalServerError", "RequestTimeout"}


def with_retry(fn: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        attempt = 0
        while True:
            try:
                return fn(*args, **kwargs)
            except ClientError as exc:
                code = exc.response.get("Error", {}).get("Code", "")
                attempt += 1
                if code not in _RETRYABLE or attempt >= MAX_ATTEMPTS:
                    raise
                delay = BASE_DELAY_SECONDS * (2 ** (attempt - 1)) + random.uniform(0, 0.25)
                time.sleep(delay)

    return wrapper
