from bson import ObjectId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from src.apps.user.models.entities import UserEntity
from src.common.messages import AUTH_MESSAGES


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        # 기존 코드의 컬렉션명 "user" 반영
        self.collection = db.get_collection("users")

    # User Info - email로 유저 정보 가져오기
    async def get_user_by_email(self, email: str) -> dict | None:
        return await self.collection.find_one({"email": email})

    # User Info - id로 유저 정보 가져오기
    async def get_user_by_id(self, user_id: str) -> dict | None:
        if not ObjectId.is_valid(user_id):
            return None
        return await self.collection.find_one({"_id": ObjectId(user_id)})

    # User 생성(C)
    async def create_user(self, user_entity: UserEntity) -> dict:
        try:
            # 1. Entity를 딕셔너리로 변환하여 DB에 삽입
            user_data = user_entity.model_dump()
            result = await self.collection.insert_one(user_data)

            # 2. 기존 코드처럼 생성된 _id를 딕셔너리에 추가하여 반환
            user_data["_id"] = result.inserted_id
            return user_data
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=AUTH_MESSAGES.SIGN_UP.FAIL.DUPLICATE,
            )

    # 마지막 로그인 기록 갱신(last_sign_in_time)
    async def last_sign_in_time(
        self, user_id: ObjectId, sign_in_time: any
    ) -> None:

        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "last_sign_in_at": sign_in_time,
                }
            },
        )
