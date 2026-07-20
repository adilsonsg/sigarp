import pytest

from app.collectors.exceptions import (
    CollectorNotFoundError,
    CollectorRegistrationError,
)
from app.collectors.registry import CollectorRegistry


class DummyCollector:
    name = "dummy"

    async def collect(self, *, endpoint: str, params=None):  # type: ignore[no-untyped-def]
        return {"endpoint": endpoint, "params": params}


def test_registry_registers_and_resolves_collector() -> None:
    registry = CollectorRegistry()
    registry.register(" Dummy ", DummyCollector)

    collector = registry.get("dummy")

    assert isinstance(collector, DummyCollector)
    assert registry.available() == ("dummy",)


def test_registry_rejects_duplicate_registration() -> None:
    registry = CollectorRegistry()
    registry.register("dummy", DummyCollector)

    with pytest.raises(CollectorRegistrationError):
        registry.register("dummy", DummyCollector)


def test_registry_rejects_unknown_collector() -> None:
    registry = CollectorRegistry()

    with pytest.raises(CollectorNotFoundError):
        registry.get("unknown")
