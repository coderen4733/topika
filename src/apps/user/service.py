from src.apps.user.repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    # 내 정보 조회(R-M) API 🔐
    async def read_me(self, current_user: dict) -> dict:
        # password 필드를 제거하고 반환
        if "password" in current_user:
            del current_user["password"]
        return current_user
