from __future__ import annotations

import asyncio
import logging
import random
from collections.abc import Awaitable, Callable, Mapping
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from time import perf_counter
from typing import Any

import httpx

from app.collectors.exceptions import (
    RemoteAPIError,
    RemoteAPIRateLimitError,
    RemoteAPITimeoutError,
)

logger = logging.getLogger(__name__)
SleepCallable = Callable[[float], Awaitable[None]]


class BaseHttpClient:
    """Reusable asynchronous HTTP client for official external data sources.

    The class centralizes connection pooling, timeout, retry, exponential backoff,
    structured logging and conversion of transport errors into SIGARP exceptions.
    Source-specific clients should subclass it and expose domain-oriented methods.
    """

    retryable_status_codes = frozenset({429, 500, 502, 503, 504})

    def __init__(
        self,
        *,
        service_name: str,
        base_url: str,
        timeout_seconds: float,
        max_retries: int,
        backoff_seconds: float,
        user_agent: str,
        client: httpx.AsyncClient | None = None,
        sleep: SleepCallable = asyncio.sleep,
    ) -> None:
        self.service_name = service_name
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self._external_client = client is not None
        self._client = client or httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=httpx.Timeout(timeout_seconds),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            headers={
                "Accept": "application/json",
                "User-Agent": user_agent,
            },
        )
        self._sleep = sleep

    async def __aenter__(self) -> BaseHttpClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def close(self) -> None:
        if not self._external_client:
            await self._client.aclose()

    async def get_json(
        self,
        endpoint: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        response = await self.request("GET", endpoint, params=params)
        try:
            return response.json()
        except ValueError as exc:
            raise RemoteAPIError(
                f"{self.service_name} returned an invalid JSON response.",
                status_code=response.status_code,
                response_body=response.text[:1000],
            ) from exc

    async def request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> httpx.Response:
        attempts = self.max_retries + 1

        for attempt in range(1, attempts + 1):
            started_at = perf_counter()
            try:
                response = await self._client.request(method, endpoint, params=params)
            except httpx.TimeoutException as exc:
                self._log_request(
                    method=method,
                    endpoint=endpoint,
                    status_code=None,
                    duration_ms=(perf_counter() - started_at) * 1000,
                    attempt=attempt,
                )
                if attempt < attempts:
                    await self._sleep(self._backoff(attempt))
                    continue
                raise RemoteAPITimeoutError(
                    f"{self.service_name} request timed out after all retry attempts."
                ) from exc
            except httpx.RequestError as exc:
                raise RemoteAPIError(
                    f"{self.service_name} request failed: {exc.__class__.__name__}."
                ) from exc

            self._log_request(
                method=method,
                endpoint=endpoint,
                status_code=response.status_code,
                duration_ms=(perf_counter() - started_at) * 1000,
                attempt=attempt,
            )

            if response.status_code in self.retryable_status_codes:
                if attempt < attempts:
                    delay = self._retry_delay(response, attempt)
                    logger.warning(
                        "external_api_retry",
                        extra={
                            "service": self.service_name,
                            "status_code": response.status_code,
                            "attempt": attempt,
                            "delay_seconds": round(delay, 2),
                        },
                    )
                    await self._sleep(delay)
                    continue
                if response.status_code == 429:
                    raise RemoteAPIRateLimitError(
                        (
                            f"{self.service_name} rate limit persisted after all "
                            "retry attempts."
                        ),
                        status_code=response.status_code,
                        response_body=response.text[:1000],
                    )

            if response.is_error:
                raise RemoteAPIError(
                    f"{self.service_name} returned an error response.",
                    status_code=response.status_code,
                    response_body=response.text[:1000],
                )

            return response

        raise RemoteAPIError(
            f"{self.service_name} request finished without a response."
        )

    def _backoff(self, attempt: int) -> float:
        return self.backoff_seconds * (2 ** (attempt - 1))

    def _retry_delay(self, response: httpx.Response, attempt: int) -> float:
        retry_after = self._parse_retry_after(response.headers.get("Retry-After"))
        if retry_after is not None:
            return max(retry_after, 1.0)

        base_delay = self._backoff(attempt)
        jitter = random.uniform(0, min(base_delay * 0.25, 5.0))
        return base_delay + jitter

    @staticmethod
    def _parse_retry_after(value: str | None) -> float | None:
        if not value:
            return None

        try:
            return max(float(value), 0.0)
        except ValueError:
            pass

        try:
            retry_at = parsedate_to_datetime(value)
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=UTC)
            return max((retry_at - datetime.now(UTC)).total_seconds(), 0.0)
        except (TypeError, ValueError, OverflowError):
            return None

    def _log_request(
        self,
        *,
        method: str,
        endpoint: str,
        status_code: int | None,
        duration_ms: float,
        attempt: int,
    ) -> None:
        logger.info(
            "external_api_request",
            extra={
                "service": self.service_name,
                "method": method,
                "path": endpoint,
                "status_code": status_code,
                "duration_ms": round(duration_ms, 2),
                "attempt": attempt,
            },
        )
