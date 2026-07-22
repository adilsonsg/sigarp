from pydantic import BaseModel

from app.security.models import AccessRole


class AuthPrincipalResponse(BaseModel):
    subject: str
    name: str
    role: AccessRole | None = None
