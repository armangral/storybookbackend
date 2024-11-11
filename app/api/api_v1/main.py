from fastapi import APIRouter

from app.api.api_v1.endpoints import chat_pdf, auth, superadmin

api_router = APIRouter()

# api_router.include_router(property.router, prefix="/property", tags=["Properties"])
api_router.include_router(superadmin.router, prefix="/superadmin", tags=["Superadmin"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(chat_pdf.router, prefix="/chatpdf", tags=["Chat PDF"])
