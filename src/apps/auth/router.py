from fastapi import APIRouter, Depends, Request, status

from src.apps.auth.dependencies import get_auth_service
from src.apps.auth.models.schemas import (
    ReTokenReq,
    ReTokenRes,
    SignInReq,
    SignInRes,
    SignUpReq,
    SignUpRes,
)
from src.apps.auth.service import AuthService
from src.common.messages import AUTH_MESSAGES
from src.core.schemas import ResSchema

# Auth Router 🚥
auth_router = APIRouter()


# 회원가입(sign-up) API
@auth_router.post(
    "/sign-up",
    response_model=ResSchema[SignUpRes],
    status_code=status.HTTP_201_CREATED,
)
async def sign_up(
    dto: SignUpReq,
    auth_service: AuthService = Depends(get_auth_service),  # DI(의존성주입)
):
    # 1. Data(Router <- Service)
    data = await auth_service.sign_up(dto)
    # 2. Response(Router -> Front)
    return {"message": AUTH_MESSAGES.SIGN_UP.SUCCESS, "data": data}


# 로그인(sign-in) API
@auth_router.post(
    "/sign-in",
    response_model=ResSchema[SignInRes],
    status_code=status.HTTP_200_OK,
)
async def sign_in(
    dto: SignInReq,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
):
    # 1. Data(Router <- Service)
    data = await auth_service.sign_in(dto, ip_address=request.client.host)
    # 2. Response(Router -> Front)
    return {"message": AUTH_MESSAGES.SIGN_IN.SUCCESS, "data": data}


# 토큰재발급(re-token) API
@auth_router.post(
    "/re-token",
    response_model=ResSchema[ReTokenRes],
    status_code=status.HTTP_200_OK,
)
async def re_token(
    dto: ReTokenReq, auth_service: AuthService = Depends(get_auth_service)
):
    # 1. Data(Router <- Service)
    data = await auth_service.re_token(dto)
    # 2. Response(Router -> Front)
    return {"message": AUTH_MESSAGES.RE_TOKEN.SUCCESS, "data": data}
