from datetime import UTC, datetime, timedelta

import bcrypt
import jwt  # pip install bcrypt pyjwt
from fastapi import HTTPException, status

from src.apps.auth.models.entities import RefreshTokenEntity
from src.apps.auth.models.schemas import ReTokenReq, SignInReq, SignUpReq
from src.apps.auth.repository import AuthRepository
from src.apps.user.models.entities import UserEntity
from src.apps.user.repository import UserRepository
from src.common.messages import AUTH_MESSAGES
from src.core.config import (
    ACCESS_TOKEN_EXPIRE,
    ACCESS_TOKEN_SECRET,
    JWT_ALGORITHM,
    REFRESH_TOKEN_EXPIRE,
    REFRESH_TOKEN_SECRET,
)


class AuthService:
    def __init__(
        self, user_repository: UserRepository, auth_repository: AuthRepository
    ):
        self.user_repository = user_repository
        self.auth_repository = auth_repository

    # 회원가입(sign-up) Business Logic
    async def sign_up(self, dto: SignUpReq) -> dict:
        # 1. email 중복 체크를 위해 조회
        is_duplicate_email = await self.user_repository.get_user_by_email(
            dto.email
        )

        # 2. 만약 중복이라면 (기존 코드의 409 예외 처리 반영)
        if is_duplicate_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=AUTH_MESSAGES.SIGN_UP.FAIL.DUPLICATE,
            )

        # 3. password 해싱(암호화)
        # bcrypt는 바이트(bytes) 타입을 입력받으므로 .encode('utf-8')이 필요
        password_bytes = dto.password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        # DB에는 문자열로 저장하기 위해 .decode('utf-8') 해주기
        hashed_password_str = hashed_password.decode("utf-8")

        # 4. 엔티티 생성 (해싱된 패스워드 주입)
        user_entity = UserEntity(
            email=dto.email,
            password=hashed_password_str,
            nickname=dto.nickname,
        )

        # 5. DB 저장 후 생성된 데이터(dict) 반환
        return await self.user_repository.create_user(user_entity)

    # 로그인(sign-in)
    async def sign_in(self, dto: SignInReq, ip_address: str) -> dict:
        # 1. user 조회
        user = await self.user_repository.get_user_by_email(dto.email)
        # 1-1. user가 없거나 비밀번호 불일치 시
        if not user or not bcrypt.checkpw(
            dto.password.encode("utf-8"), user["password"].encode("utf-8")
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AUTH_MESSAGES.SIGN_IN.FAIL.INVALID,
            )

        # 2. Token 생성
        now = datetime.now(UTC)
        # 2-1. Access Token (기본값: 30분)
        access_expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE)
        access_payload = {
            "sub": str(user["_id"]),
            "type": "access",
            "exp": access_expire,
        }
        access_token = jwt.encode(
            access_payload, ACCESS_TOKEN_SECRET, algorithm=JWT_ALGORITHM
        )
        # 2-2. Refresh Token (기본값: 14일)
        refresh_expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE)
        refresh_payload = {
            "sub": str(user["_id"]),
            "type": "refresh",
            "exp": refresh_expire,
        }
        refresh_token = jwt.encode(
            refresh_payload, REFRESH_TOKEN_SECRET, algorithm=JWT_ALGORITHM
        )

        # 3. 엔티티 생성
        refresh_token_entity = RefreshTokenEntity(
            user_id=str(user["_id"]),
            ip_address=ip_address,
            refresh_token=refresh_token,
        )

        # 4. Refresh Token을 DB의 해당 유저 문서에 저장
        await self.auth_repository.create_refresh_token(refresh_token_entity)

        # 5. 로그인 일시 기록
        await self.user_repository.last_sign_in_time(
            refresh_token_entity.user_id, now
        )

        # 6. Response
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    #

    # Refresh Token 재발급
    async def re_token(self, dto: ReTokenReq) -> dict:
        try:
            # 1. Refresh Token 디코딩
            payload = jwt.decode(
                dto.refresh_token,
                REFRESH_TOKEN_SECRET,
                algorithms=[JWT_ALGORITHM],
            )
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type")
            # 1-1. 해당 user_id가 없거나 토큰 타입이 "refresh"가 아닌 경우
            if user_id is None or token_type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=AUTH_MESSAGES.RE_TOKEN.FAIL.INVALID,
                )

            # 2. DB에 저장된 토큰과 일치하는지 확인 (중요: 보안 강화)
            user = await self.user_repository.get_user_by_id(user_id)
            refresh_token = (
                await self.auth_repository.get_refresh_token_by_refresh_token(
                    dto.refresh_token
                )
            )
            # 2-1. 만약 해당 user가 없거나 토큰 소유 user가 일치하지 않는 경우
            print("요청 : ", user_id, "토큰 속 : ", refresh_token["user_id"])
            if user is None or user_id != refresh_token["user_id"]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=AUTH_MESSAGES.RE_TOKEN.FAIL.UNAUTHORIZED,
                )

            # 3. 새로운 Access Token 발행
            now = datetime.now(UTC)
            access_expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE)
            new_access_token = jwt.encode(
                {"sub": user_id, "type": "access", "exp": access_expire},
                ACCESS_TOKEN_SECRET,
                algorithm=JWT_ALGORITHM,
            )

            # 4. Response
            return {"access_token": new_access_token, "token_type": "bearer"}
        except jwt.ExpiredSignatureError:  # 리프레시 토큰 만료기간이 지났을 때
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AUTH_MESSAGES.RE_TOKEN.FAIL.EXPIRED,
            )
        except jwt.PyJWTError:  # 토큰이 위조되었거나 변조되었을 때
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AUTH_MESSAGES.RE_TOKEN.FAIL.SESSION,
            )
