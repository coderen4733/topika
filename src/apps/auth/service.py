from datetime import UTC, datetime, timedelta

import bcrypt
import jwt  # pip install bcrypt pyjwt
from fastapi import HTTPException, status

from src.apps.auth.models.schemas import ReTokenReq, SignInReq, SignUpReq
from src.apps.user.models.entities import UserEntity
from src.apps.user.repository import UserRepository
from src.core.config import (
    ACCESS_TOKEN_EXPIRE,
    ACCESS_TOKEN_SECRET,
    JWT_ALGORITHM,
    REFRESH_TOKEN_EXPIRE,
    REFRESH_TOKEN_SECRET,
)


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

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
                detail="이미 가입된 이메일입니다.",
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
    async def sign_in(self, dto: SignInReq) -> dict:
        # 1. user 조회
        user = await self.user_repository.get_user_by_email(dto.email)
        # 1-1. user가 없거나 비밀번호 불일치 시
        if not user or not bcrypt.checkpw(
            dto.password.encode("utf-8"), user["password"].encode("utf-8")
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 일치하지 않습니다.",
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

        # 3. Refresh Token을 DB의 해당 유저 문서에 저장
        await self.user_repository.re_token(user["_id"], refresh_token, now)

        # 4. Response
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
                    detail="유효하지 않은 리프레시 토큰입니다.",
                )

            # 2. DB에 저장된 토큰과 일치하는지 확인 (중요: 보안 강화)
            user = await self.user_repository.get_user_by_id(user_id)
            # 2-1. 만약 해당 user가 없거나 저장된 리프레시 토큰이 없는 경우
            if user is None or user.get("refresh_token") != dto.refresh_token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="만료되었거나 유효하지 않은 리프레시 토큰입니다.",
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
                detail="리프레시 토큰이 만료되었습니다.",
            )
        except jwt.PyJWTError:  # 토큰이 위조되었거나 변조되었을 때
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="인증 세션이 유효하지 않습니다.",
            )
