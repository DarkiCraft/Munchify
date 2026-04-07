import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from models.user import UserModel
from repos.user import UserRepo
from schemas.auth import SignupRequest, LoginRequest, SignupResponse, LoginResponse

JWT_KEY = os.getenv("JWT_KEY")


class AuthService:
    def __init__(self, user_repo: UserRepo):
        self.__repo = user_repo

    def __login(self, email: str, password: str):
        user = self.__repo.get_by_email(email)
        if not user:
            raise ValueError("User not found")
        if not bcrypt.checkpw(password.encode(), user.password_hash):
            raise ValueError("Incorrect password")
        return LoginResponse(access_token=jwt.encode({
                "user_id": user.user_id,
                "exp": datetime.now(timezone.utc) + timedelta(days=1)
            },
            JWT_KEY, algorithm="HS256")
        )

    def signup(self, request: SignupRequest):
        # currently handles user creations directly
        # split into separate service later??
        user = self.__repo.create(
            UserModel(
                user_name=request.user_name,
                email=request.email,
                password_hash=bcrypt.hashpw(request.password.encode(), bcrypt.gensalt()),
                signup_date=datetime.now()
            )
        )
        return SignupResponse(
            user_id=user.user_id,
            user_name=user.user_name,
            email=user.email
        )

    def login(self, request: LoginRequest):
        return self.__login(request.email, request.password)
