from fastapi import Depends
from sqlmodel import Session
from typing import Annotated
from database import get_db, engine
from fastapi import Request
from sqlmodel import select
from models import User
db_dependency = Annotated[Session, Depends(get_db)]
from passlib.context import CryptContext



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)



# Fetch the current logged-in user from the DB
def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    with Session(engine) as session:
    
        if user_id:
            statement = select(User).where(User.id == user_id)
            user = session.exec(statement).first()
            return user
        return None  # User is not logged in