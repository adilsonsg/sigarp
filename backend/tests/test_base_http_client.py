from collections.abc import Awaitable, Callable

import httpx
import pytest

from app.clients.base import BaseHttpClient
from app.collectors.exceptions import RemoteAPIError


def no_sleep(delays: list[float]) -> Callable[[float], Awaitable[None]]:
    async def sleeper(delay: float) -> None:
        delays.append(delay)

    return sleeper


@pytest.mark.asyncio
async def test_base_client_retries_transient_error_and_decodes_json() -> None:
    calls = 0
    delays: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        status = 503 if calls == 1 else 200
        return httpx.Response(status, json={"ok": True}, request=request)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        base_url="https://example.test", transport=transport
    ) as http_client:
        client = BaseHttpClient(
            service_name="Example",
            base_url="https://example.test",
            timeout_seconds=1,
            max_retries=1,
            backoff_seconds=0.25,
            user_agent="SIGARP-Test",
            client=http_client,
            sleep=no_sleep(delays),
        )
        result = await client.get_json("/resource")

    assert result == {"ok": True}
    assert calls == 2
    assert len(delays) == 1
    assert 0.25 <= delays[0] <= 0.3125


@pytest.mark.asyncio
async def test_base_client_rejects_invalid_json() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, text="invalid", request=request)
    )
    async with httpx.AsyncClient(
        base_url="https://example.test", transport=transport
    ) as http_client:
        client = BaseHttpClient(
            service_name="Example",
            base_url="https://example.test",
            timeout_seconds=1,
            max_retries=0,
            backoff_seconds=0.25,
            user_agent="SIGARP-Test",
            client=http_client,
        )
        with pytest.raises(RemoteAPIError):
            await client.get_json("/resource")


@pytest.mark.asyncio
async def test_base_client_respects_retry_after_header() -> None:
    calls = 0
    delays: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(429, headers={"Retry-After": "60"}, request=request)
        return httpx.Response(200, json={"ok": True}, request=request)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        base_url="https://example.test", transport=transport
    ) as http_client:
        client = BaseHttpClient(
            service_name="Example",
            base_url="https://example.test",
            timeout_seconds=1,
            max_retries=1,
            backoff_seconds=5,
            user_agent="SIGARP-Test",
            client=http_client,
            sleep=no_sleep(delays),
        )
        result = await client.get_json("/resource")

    assert result == {"ok": True}
    assert calls == 2
    assert delays == [60.0]
