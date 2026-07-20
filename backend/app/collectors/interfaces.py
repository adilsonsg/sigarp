from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Collector(Protocol):
    """Contract implemented by every SIGARP collector."""

    name: str

    async def collect(
        self,
        *,
        endpoint: str,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        """Collect data from the source and return the decoded response."""
