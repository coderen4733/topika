from datetime import UTC, datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.apps.user.models.enums import SignInType, UserRole


class UserEntity(BaseModel):
    # 기본 정보
    email: str
    nickname: str
    password: str

    # 시스템 및 권한
    role: UserRole = Field(
        default=UserRole.USER, description="권한[user, admin]"
    )
    sign_in_type: SignInType = Field(
        default=SignInType.EMAIL,
        description="가입경로[email, naver, kakao, google]",
    )
    is_active: bool = True

    # 시간 메타데이터
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_sign_in_at: Optional[datetime] = Field(
        default=None, description="최근 로그인 일시"
    )
