from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.apps.user.models.entities import UserEntity


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        # 기존 코드의 컬렉션명 "user" 반영
        self.collection = db.get_collection("user")

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
        # 1. Entity를 딕셔너리로 변환하여 DB에 삽입
        user_data = user_entity.model_dump()
        result = await self.collection.insert_one(user_data)

        # 2. 기존 코드처럼 생성된 _id를 딕셔너리에 추가하여 반환
        user_data["_id"] = result.inserted_id
        return user_data

    # 리프레시 토큰(re_token)
    async def re_token(
        self, user_id: ObjectId, refresh_token: str, sign_in_time: any
    ) -> None:
        await self.collection.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "refresh_token": refresh_token,
                    "last_sign_in_at": sign_in_time,
                }
            },
        )
