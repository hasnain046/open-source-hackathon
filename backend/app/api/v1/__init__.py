# Package: app.api.v1
# Description: Version 1 API router compilation, linking prefixes to sub-module routes.

from fastapi import APIRouter

# Import sub-routers
from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.forecasting import router as forecasting_router
from app.api.v1.cpi import router as cpi_router
from app.api.v1.trends import router as trends_router
from app.api.v1.news import router as news_router
from app.api.v1.currency import router as currency_router
from app.api.v1.copilot import router as copilot_router
from app.api.v1.heatmap import router as heatmap_router
from app.api.v1.simulator import router as simulator_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.profile import router as profile_router
from app.api.v1.admin import router as admin_router
from app.api.v1.rag import router as rag_router

api_router = APIRouter()

# Include routes with prefixes
api_router.include_router(auth_router)
api_router.include_router(dashboard_router)
api_router.include_router(forecasting_router)
api_router.include_router(cpi_router)
api_router.include_router(trends_router)
api_router.include_router(news_router)
api_router.include_router(currency_router)
api_router.include_router(copilot_router)
api_router.include_router(heatmap_router)
api_router.include_router(simulator_router)
api_router.include_router(alerts_router)
api_router.include_router(profile_router)
api_router.include_router(admin_router)
api_router.include_router(rag_router)
