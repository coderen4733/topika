from fastapi import APIRouter, Depends, status

from src.apps.auth.dependencies import get_auth_service
from src.apps.auth.models.schemas import (
    ReTokenReq,
    ReTokenRes,
    SignInReq,
    SignInRes,
    SignUpReq,
)
from src.apps.auth.service import AuthService

# Auth Router 🚥
auth_router = APIRouter()


# 회원가입(sign-up) API
@auth_router.post(
    "/sign-up", response_model=SignUpReq, status_code=status.HTTP_201_CREATED
)
async def sign_up(
    dto: SignUpReq,
    auth_service: AuthService = Depends(get_auth_service),  # DI(의존성주입)
):
    # 1. 회원가입 비즈니스 로직 실행 (결과물은 _id가 포함된 dict)
    created_user_dict = await auth_service.sign_up(dto)
    # 2. Response 반환 (FastAPI가 response_model을 참조, _id를 id 필드로 매핑)
    return created_user_dict


# 로그인(sign-in) API
@auth_router.post(
    "/sign-in", response_model=SignInRes, status_code=status.HTTP_200_OK
)
async def sign_in(
    dto: SignInReq, auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.sign_in(dto)


# 토큰재발급(re-token) API
@auth_router.post(
    "/re-token", response_model=ReTokenRes, status_code=status.HTTP_200_OK
)
async def re_token(
    dto: ReTokenReq, auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.re_token(dto)
