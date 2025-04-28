from fastapi import APIRouter

from app.api.endpoints import auth, files, reports, rules, schedules

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(rules.router, prefix="/rules", tags=["rules"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
