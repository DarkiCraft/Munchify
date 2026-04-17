from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.activity import router as activity_router
from controllers.admin import router as admin_router
from controllers.auth import router as auth_router
from controllers.recommend import router as recommend_router
from models.base import Base
from database import engine

Base.metadata.create_all(engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(activity_router)
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(recommend_router)
