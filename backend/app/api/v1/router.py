from fastapi import APIRouter

from app.api.responses import COMMON_ERROR_RESPONSES
from app.api.routes.auth import router as auth_router
from app.api.routes.pncp import router as pncp_router
from app.api.routes.system import router as system_router
from app.api.v1.routes.opportunities import router as opportunities_router
from app.api.v1.routes.organizations import router as organizations_router
from app.api.v1.routes.price_registries import router as price_registries_router

router = APIRouter(prefix="/api/v1")

router.include_router(
    system_router,
    responses=COMMON_ERROR_RESPONSES,
)
router.include_router(
    auth_router,
    responses=COMMON_ERROR_RESPONSES,
)
router.include_router(organizations_router)
router.include_router(
    pncp_router,
    responses=COMMON_ERROR_RESPONSES,
)
router.include_router(opportunities_router)
router.include_router(price_registries_router)
