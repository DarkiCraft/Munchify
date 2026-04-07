import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists

DATABASE_URL = os.getenv("DATABASE_URL")

if not database_exists(DATABASE_URL):
    create_database(DATABASE_URL)

engine = create_engine(DATABASE_URL)
session_local = sessionmaker(bind=engine)
