import os

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import session_local
from repos.interaction import InteractionRepo
from repos.item import ItemRepo
from repos.order import OrderRepo
from repos.rating import RatingRepo
from repos.user import UserRepo
from services.activity import ActivityService
from services.auth import AuthService
from services.recommend import RecommendationService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> int:
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


def get_interaction_repo(db: Session = Depends(get_db)):
    return InteractionRepo(db)

def get_item_repo(db: Session = Depends(get_db)):
    return ItemRepo(db)

def get_order_repo(db: Session = Depends(get_db)):
    return OrderRepo(db)

def get_rating_repo(db: Session = Depends(get_db)):
    return RatingRepo(db)

def get_user_repo(db: Session = Depends(get_db)):
    return UserRepo(db)


def get_auth_service(repo: UserRepo = Depends(get_user_repo)):
    return AuthService(repo)

def get_activity_service(
        interaction_repo: InteractionRepo = Depends(get_interaction_repo),
        item_repo: ItemRepo = Depends(get_item_repo),
        order_repo: OrderRepo = Depends(get_order_repo),
        rating_repo: RatingRepo = Depends(get_rating_repo)
):
    return ActivityService(
        interaction_repo,
        item_repo,
        order_repo,
        rating_repo
    )

def get_recommendation_service(
        interaction_repo: InteractionRepo = Depends(get_interaction_repo),
        item_repo: ItemRepo = Depends(get_item_repo),
        user_repo: UserRepo = Depends(get_user_repo)
):
    return RecommendationService(
        interaction_repo,
        item_repo,
        user_repo
    )
