from fastapi import FastAPI
from app.api.routes.organizations import router as organizations_router
from app.core.config import settings

app = FastAPI(title=f"{settings.app_name} API", version=settings.app_version, description="Sistema Inteligente de Gestão e Análise de Registro de Preços")
app.include_router(organizations_router)

@app.get("/health", tags=["Sistema"])
def health() -> dict[str, str]:
    return {"application": settings.app_name, "version": settings.app_version, "status": "online"}
