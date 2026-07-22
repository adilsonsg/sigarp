from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.auth import AuthPrincipalResponse
from app.security.authentication import authenticate_principal
from app.security.models import AuthenticatedPrincipal

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.get("/me", response_model=AuthPrincipalResponse)
def get_authenticated_principal(
    principal: Annotated[AuthenticatedPrincipal, Depends(authenticate_principal)],
) -> AuthPrincipalResponse:
    return AuthPrincipalResponse(
        subject=principal.subject,
        name=principal.name,
        role=principal.role,
    )
