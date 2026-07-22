import hashlib
import hmac
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.core.exceptions import AccessDeniedError, AuthenticationRequiredError
from app.security.models import AccessRole, AuthenticatedPrincipal

bearer_scheme = HTTPBearer(auto_error=False)


def authenticate_principal(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Security(bearer_scheme),
    ] = None,
) -> AuthenticatedPrincipal:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthenticationRequiredError()

    received_hash = hashlib.sha256(credentials.credentials.encode("utf-8")).hexdigest()
    for configured in settings.auth_principals:
        if hmac.compare_digest(received_hash, configured.token_sha256):
            return AuthenticatedPrincipal(
                subject=configured.subject,
                name=configured.name,
                role=configured.role,
            )
    raise AuthenticationRequiredError("Token de acesso inválido.")


def require_minimum_role(
    minimum_role: AccessRole,
) -> Callable[[AuthenticatedPrincipal], AuthenticatedPrincipal]:
    def dependency(
        principal: Annotated[
            AuthenticatedPrincipal,
            Depends(authenticate_principal),
        ],
    ) -> AuthenticatedPrincipal:
        if principal.role is None or principal.role.level < minimum_role.level:
            raise AccessDeniedError()
        return principal

    return dependency
