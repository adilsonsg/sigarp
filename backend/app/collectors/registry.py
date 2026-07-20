from collections.abc import Callable

from app.collectors.exceptions import (
    CollectorNotFoundError,
    CollectorRegistrationError,
)
from app.collectors.interfaces import Collector

CollectorFactory = Callable[[], Collector]


class CollectorRegistry:
    """Registry that resolves collectors without source-specific conditionals."""

    def __init__(self) -> None:
        self._factories: dict[str, CollectorFactory] = {}

    def register(
        self,
        name: str,
        factory: CollectorFactory,
        *,
        replace: bool = False,
    ) -> None:
        normalized_name = self._normalize(name)
        if normalized_name in self._factories and not replace:
            raise CollectorRegistrationError(
                f"Collector '{normalized_name}' is already registered."
            )
        self._factories[normalized_name] = factory

    def get(self, name: str) -> Collector:
        normalized_name = self._normalize(name)
        try:
            factory = self._factories[normalized_name]
        except KeyError as exc:
            raise CollectorNotFoundError(
                f"Collector '{normalized_name}' is not registered."
            ) from exc
        return factory()

    def available(self) -> tuple[str, ...]:
        return tuple(sorted(self._factories))

    @staticmethod
    def _normalize(name: str) -> str:
        normalized_name = name.strip().lower()
        if not normalized_name:
            raise CollectorRegistrationError("Collector name cannot be empty.")
        return normalized_name


collector_registry = CollectorRegistry()
