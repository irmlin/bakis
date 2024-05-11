from typing import Union

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt

from ..models import User
from ..schemas import Token
from ..settings import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM


class AuthService:
    def __init__(self):
        self.__pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def login(self, form_data: OAuth2PasswordRequestForm, db: Session):
        user = self.__authenticate_user(username=form_data.username, password=form_data.password, db=db)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.__create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")

    def __authenticate_user(self, username: str, password: str, db: Session):
        db_user = db.query(User).filter(User.username == username).first()
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect/non-existent username!",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not self.__verify_password(password, db_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password!",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return db_user

    def __verify_password(self, plain_password, hashed_password) -> bool:
        return self.__pwd_context.verify(plain_password, hashed_password)

    def __get_password_hash(self, password) -> str:
        return self.__pwd_context.hash(password)

    def __create_access_token(self, data: dict, expires_delta: Union[timedelta, None] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
