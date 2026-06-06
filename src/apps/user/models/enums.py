from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class SignInType(str, Enum):
    EMAIL = "email"
    NAVER = "naver"
    KAKAO = "kakao"
    GOOGLE = "google"
