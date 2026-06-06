from fastapi import APIRouter, Depends, status

from src.apps.user.dependencies import get_current_user, get_user_repository
from src.apps.user.models.schemas import UserMeRes
from src.apps.user.repository import UserRepository
from src.apps.user.service import UserService
from src.common.messages import USER_MESSAGES
from src.core.schemas import ResSchema

# User Router 🚥
user_router = APIRouter()


# 공통 UserService 조립 공장 함수
def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repository=user_repository)


# 내 정보 조회(R-M) API 🔐
@user_router.get(
    "/me", response_model=ResSchema[UserMeRes], status_code=status.HTTP_200_OK
)
async def read_me(
    current_user: dict = Depends(
        get_current_user
    ),  # 👈 인증 의존성 주입 완료!
    user_service: UserService = Depends(get_user_service),
):
    # 1. Data(Router <- Service)
    data = await user_service.read_me(current_user)
    return {"message": USER_MESSAGES.READ_ME.SUCCESS, "data": data}
