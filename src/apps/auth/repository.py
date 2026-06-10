from bson import ObjectId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from src.apps.auth.models.entities import RefreshTokenEntity
from src.common.messages import AUTH_MESSAGES


class AuthRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.get_collection("refresh_tokens")

    # 리프레시 토큰 있는지 확인하기
    async def get_refresh_token_by_refresh_token(
        self, refresh_token: str
    ) -> dict | None:
        return await self.collection.find_one({"refresh_token": refresh_token})

    # 특정 user_id로 리프레시 토큰 있는지 확인하기
    async def get_refresh_token_by_user_id(self, user_id: str) -> dict | None:
        if not ObjectId.is_valid(user_id):
            return None
        return await self.collection.find_one({"user_id": ObjectId(user_id)})

    # RefreshToken 생성(C)
    async def create_refresh_token(
        self, refresh_token_entity: RefreshTokenEntity
    ) -> dict:
        try:
            # 1. Pydantic 모델을 MongoDB에 저장할 수 있도록 딕셔너리로 변환
            # (Pydantic v2 기준 model_dump() 사용, v1의 경우 dict() 사용)
            token_dict = refresh_token_entity.model_dump()

            # 2. MongoDB에 데이터 삽입
            result = await self.collection.insert_one(token_dict)

            # 3. 삽입된 데이터의 _id(ObjectId)를 딕셔너리에 추가하여 반환
            token_dict["_id"] = result.inserted_id
            return token_dict

        except DuplicateKeyError:
            # 데이터베이스 레벨에서 unique 제약 조건(중복)에 걸렸을 때 예외 처리
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=AUTH_MESSAGES.RE_TOKEN.FAIL.DUPLICATED,
            )
