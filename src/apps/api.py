from fastapi import APIRouter

from src.apps.auth.router import auth_router
from src.apps.user.router import user_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(user_router, prefix="/users", tags=["User"])
