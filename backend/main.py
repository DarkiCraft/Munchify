from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from controllers.activity import router as activity_router
from controllers.auth import router as auth_router
from controllers.recommend import router as recommend_router
from models.base import Base
from database import engine

Base.metadata.create_all(engine)

app = FastAPI()
app.include_router(activity_router)
app.include_router(auth_router)
app.include_router(recommend_router)
