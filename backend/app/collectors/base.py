from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any


class BaseCollector(ABC):
    """Base class for official data-source collectors."""

    name: str

    @abstractmethod
    async def collect(
        self,
        *,
        endpoint: str,
        params: Mapping[str, Any] | None = None,
    ) -> Any:
        """Collect data from the source and return the decoded response."""
