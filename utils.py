from fastapi import Depends
from sqlmodel import Session
from typing import Annotated
from database import get_db
db_dependency = Annotated[Session, Depends(get_db)]
from passlib.context import CryptContext



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)