from app.config import settings
from app.routers import (device_router, distribution_router, placement_router,
                         rack_router)
from fastapi import APIRouter, FastAPI

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="REST API for managing data center racks and devices",
    docs_url="/docs",
    redoc_url="/redoc",
)

# API v1 router
api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(device_router.router)
api_v1_router.include_router(rack_router.router)
api_v1_router.include_router(placement_router.router)
api_v1_router.include_router(distribution_router.router)
app.include_router(api_v1_router)


@app.get("/api/v1/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
    }
