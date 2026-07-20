import asyncio
import logging
from collections.abc import Awaitable, Callable, Mapping
from time import perf_counter
from typing import Any

import httpx

from app.collectors.exceptions import (
    RemoteAPIError,
    RemoteAPIRateLimitError,
    RemoteAPITimeoutError,
)
from app.collectors.pncp.config import PNCPConfig

logger = logging.getLogger(__name__)
SleepCallable = Callable[[float], Awaitable[None]]


class PNCPClient:
    """Asynchronous client for the official PNCP Consulta API."""

    retryable_status_codes = frozenset({429, 500, 502, 503, 504})

    def __init__(
        self,
        config: PNCPConfig | None = None,
        *,
        client: httpx.AsyncClient | None = None,
        sleep: SleepCallable = asyncio.sleep,
    ) -> None:
        self.config = config or PNCPConfig.from_settings()
        self._external_client = client is not None
        self._client = client or httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=httpx.Timeout(self.config.timeout_seconds),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            headers={
                "Accept": "application/json",
                "User-Agent": self.config.user_agent,
            },
        )
        self._sleep = sleep

    async def __aenter__(self) -> "PNCPClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def close(self) -> None:
        if not self._external_client:
            await self._client.aclose()

    async def get(
        self,
        endpoint: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        response = await self._request("GET", endpoint, params=params)
        try:
            return response.json()
        except ValueError as exc:
            raise RemoteAPIError(
                "PNCP returned an invalid JSON response.",
                status_code=response.status_code,
                response_body=response.text[:1000],
            ) from exc

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> httpx.Response:
        attempts = self.config.max_retries + 1

        for attempt in range(1, attempts + 1):
            started_at = perf_counter()
            try:
                response = await self._client.request(
                    method,
                    endpoint,
                    params=params,
                )
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
                    "PNCP request timed out after all retry attempts."
                ) from exc
            except httpx.RequestError as exc:
                raise RemoteAPIError(
                    f"PNCP request failed: {exc.__class__.__name__}."
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
                    await self._sleep(self._backoff(attempt))
                    continue
                if response.status_code == 429:
                    raise RemoteAPIRateLimitError(
                        "PNCP rate limit persisted after all retry attempts.",
                        status_code=response.status_code,
                        response_body=response.text[:1000],
                    )

            if response.is_error:
                raise RemoteAPIError(
                    "PNCP returned an error response.",
                    status_code=response.status_code,
                    response_body=response.text[:1000],
                )

            return response

        raise RemoteAPIError("PNCP request finished without a response.")

    def _backoff(self, attempt: int) -> float:
        return self.config.backoff_seconds * (2 ** (attempt - 1))

    @staticmethod
    def _log_request(
        *,
        method: str,
        endpoint: str,
        status_code: int | None,
        duration_ms: float,
        attempt: int,
    ) -> None:
        logger.info(
            "pncp_request",
            extra={
                "method": method,
                "path": endpoint,
                "status_code": status_code,
                "duration_ms": round(duration_ms, 2),
                "attempt": attempt,
            },
        )
