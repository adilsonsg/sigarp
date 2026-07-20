from collections.abc import Awaitable, Callable

import httpx
import pytest

from app.collectors.exceptions import (
    RemoteAPIError,
    RemoteAPIRateLimitError,
    RemoteAPITimeoutError,
)
from app.collectors.pncp.client import PNCPClient
from app.collectors.pncp.config import PNCPConfig


@pytest.fixture
def config() -> PNCPConfig:
    return PNCPConfig(
        base_url="https://pncp.test",
        timeout_seconds=1,
        max_retries=2,
        backoff_seconds=0.01,
        user_agent="SIGARP-Test",
    )


def no_sleep(delays: list[float]) -> Callable[[float], Awaitable[None]]:
    async def sleeper(delay: float) -> None:
        delays.append(delay)

    return sleeper


@pytest.mark.asyncio
async def test_client_returns_decoded_json(config: PNCPConfig) -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json={"data": [1]}, request=request)
    )
    async with httpx.AsyncClient(
        base_url=config.base_url, transport=transport
    ) as http_client:
        client = PNCPClient(config, client=http_client)
        result = await client.get("/v1/atas", params={"pagina": 1})

    assert result == {"data": [1]}


@pytest.mark.asyncio
async def test_client_retries_with_exponential_backoff(config: PNCPConfig) -> None:
    calls = 0
    delays: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        status = 503 if calls < 3 else 200
        return httpx.Response(status, json={"ok": True}, request=request)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        base_url=config.base_url, transport=transport
    ) as http_client:
        client = PNCPClient(
            config,
            client=http_client,
            sleep=no_sleep(delays),
        )
        result = await client.get("/v1/atas")

    assert result == {"ok": True}
    assert calls == 3
    assert delays == [0.01, 0.02]


@pytest.mark.asyncio
async def test_client_raises_rate_limit_after_retries(config: PNCPConfig) -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(429, text="limit", request=request)
    )
    async with httpx.AsyncClient(
        base_url=config.base_url, transport=transport
    ) as http_client:
        client = PNCPClient(config, client=http_client, sleep=no_sleep([]))
        with pytest.raises(RemoteAPIRateLimitError) as exc_info:
            await client.get("/v1/atas")

    assert exc_info.value.status_code == 429


@pytest.mark.asyncio
async def test_client_raises_timeout_after_retries(config: PNCPConfig) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timeout", request=request)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        base_url=config.base_url, transport=transport
    ) as http_client:
        client = PNCPClient(config, client=http_client, sleep=no_sleep([]))
        with pytest.raises(RemoteAPITimeoutError):
            await client.get("/v1/atas")


@pytest.mark.asyncio
async def test_client_rejects_invalid_json(config: PNCPConfig) -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, text="not-json", request=request)
    )
    async with httpx.AsyncClient(
        base_url=config.base_url, transport=transport
    ) as http_client:
        client = PNCPClient(config, client=http_client)
        with pytest.raises(RemoteAPIError):
            await client.get("/v1/atas")
