from fastapi import APIRouter

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.catalog import router as catalog_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.circulation import router as circulation_router
from app.api.v1.endpoints.uploads import router as uploads_router

router = APIRouter()
router.include_router(health_router)
router.include_router(catalog_router)
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(circulation_router)
router.include_router(uploads_router)
