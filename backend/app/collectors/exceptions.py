class CollectorError(Exception):
    """Base exception for data collectors."""


class CollectorNotFoundError(CollectorError):
    """Raised when a collector is not registered."""


class CollectorRegistrationError(CollectorError):
    """Raised when a collector cannot be registered."""


class RemoteAPIError(CollectorError):
    """Raised when a remote API returns an unexpected response."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class RemoteAPITimeoutError(RemoteAPIError):
    """Raised when a remote API request exceeds the configured timeout."""


class RemoteAPIRateLimitError(RemoteAPIError):
    """Raised when a remote API keeps returning HTTP 429."""
