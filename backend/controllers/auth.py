from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from dependencies import get_auth_service
from schemas.auth import SignupRequest, LoginRequest, SignupResponse, LoginResponse
from services.auth import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=SignupResponse)
def signup(request: SignupRequest, service: AuthService = Depends(get_auth_service)):
    return service.signup(request)


@router.post("/login", response_model=LoginResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service)
):
    return service.login(LoginRequest(email=form_data.username, password=form_data.password))