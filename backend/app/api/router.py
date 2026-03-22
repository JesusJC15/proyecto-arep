from fastapi import APIRouter

from app.api.routes import auth, consultations, meta, professional_cases


api_router = APIRouter()
api_router.include_router(meta.router)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(consultations.router, prefix="/consultations", tags=["consultations"])
api_router.include_router(
    professional_cases.router,
    prefix="/professional/cases",
    tags=["professional-cases"],
)
