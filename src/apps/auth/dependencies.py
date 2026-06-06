from fastapi import Request

from src.apps.auth.service import AuthService
from src.apps.user.repository import UserRepository


# 1. DB 인스턴스를 주입받아 Repository를 생성하는 함수
def get_user_repository(request: Request) -> UserRepository:
    return UserRepository(db=request.app.mongodb)


# 2. Repository를 주입받아 Service를 생성하는 함수
def get_auth_service(request: Request) -> AuthService:
    repository = get_user_repository(request)
    return AuthService(user_repository=repository)
