import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader

from src.apps.user.repository import UserRepository
from src.core.config import ACCESS_TOKEN_SECRET, JWT_ALGORITHM

# 방식1: OAuth2PasswordBearer 방식으로 로그인 경로를 지정
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
# 방식2: APIKeyHeader 방식으로 HTTP 헤더의 Authorization 필드를 직접 제어
oauth2_scheme = APIKeyHeader(name="Authorization", auto_error=False)


# 1. 공통으로 사용할 UserRepository 공장 함수
def get_user_repository(request: Request) -> UserRepository:
    return UserRepository(db=request.app.mongodb)


# 2. 인증용 공통 의존성 함수 🔐 (라우터에서 Depends로 호출할 핵심 함수)
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repository: UserRepository = Depends(get_user_repository),
) -> dict:
    # 토큰이 헤더에 아예 없는 경우 예외 처리
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 토큰이 누락되었습니다.",
        )

    try:
        # 0. APIKeyHeader 방식인 경우 => 헤더에 Bearer 분리 처리
        if token.lower().startswith("bearer "):
            parts = token.split(" ")
            if len(parts) == 2:
                token = parts[1]
            else:
                token = parts[0]

        # 1. 페이로드에서 필요한 정보 추출
        payload = jwt.decode(
            token, ACCESS_TOKEN_SECRET, algorithms=[JWT_ALGORITHM]
        )
        user_id = payload.get("sub")

        # 1-1. 만약 토큰 타입이 "access"가 아니면
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access Token이 아닙니다.",
            )

        # 2. 페이로드에 담긴 user_id로 사용자 조회
        user = await user_repository.get_user_by_id(user_id)

        # 2-1. 만약 사용자가 없는 경우
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="존재하지 않는 사용자입니다.",
            )

        # 3. 해당 사용자 정보 전달
        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰 세션이 만료되었습니다.",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
        )
    except Exception as err:
        raise err
