from typing import Optional
from sqlmodel import SQLModel, Field
import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: Optional[str] = Field(default=None, unique=True)
    phone: Optional[str] = Field(default=None, unique=True)
    password: str
    created_at: str = Field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

class File(SQLModel, table=True):
    id: str = Field(primary_key=True)
    user_id: Optional[int] = Field(default=None, index=True)
    name: str
    path: str
    mime: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

class Chat(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, index=True)
    role: str
    text: str
    ts: str = Field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

class Memory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, index=True)
    text: str
    embedding_json: Optional[str] = ""
    created_at: str = Field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
