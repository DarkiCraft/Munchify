from pydantic import BaseModel, EmailStr


class SignupRequest(BaseModel):
    user_name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupResponse(BaseModel):
    user_id: int
    user_name: str
    email: EmailStr


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
