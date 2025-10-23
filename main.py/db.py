from sqlmodel import SQLModel, create_engine, Session
from .models import User, File, Chat, Memory
from typing import Optional
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mora_multilang_sql.db")
engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    SQLModel.metadata.create_all(engine)

# convenience session creator for sync usage
def get_session() -> Session:
    return Session(engine)
