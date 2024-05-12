from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing_extensions import Annotated

from ..dependencies import get_current_user, get_db
from ..schemas import UserRead
from ..services import AuthService


class AuthController:

    def __init__(self):
        self.router = APIRouter(tags=["auth"], prefix="/auth")
        self.auth_service = AuthService()

        self.__init_routes(router=self.router)

    def __init_routes(self, router):
        @router.post("/login")
        async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
            return self.auth_service.login(form_data=form_data, db=db)

        @router.get("/user", response_model=UserRead)
        async def user(current_user: Annotated[str, Depends(get_current_user)]):
            return current_user
