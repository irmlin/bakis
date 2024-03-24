from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..schemas import UserCreate, UserRead, UserUpdate
from ..services import UserService


class UserController:

    def __init__(self):
        self.router = APIRouter(tags=["user"], prefix="/users")
        self.user_service = UserService()

        self.__init_routes(router=self.router)

    def __init_routes(self, router):
        @router.post("/", response_model=UserRead)
        def create_user(user_create: UserCreate, db: Session = Depends(get_db)):
            return self.user_service.create_user(db=db, user_create=user_create)

        @router.get("/", response_model=List[UserRead])
        def get_users(db: Session = Depends(get_db)):
            return self.user_service.get_users(db)

        @router.get("/{user_id}", response_model=UserRead)
        def get_user(user_id: int, db: Session = Depends(get_db)):
            return self.user_service.get_user(db, user_id=user_id)

        @router.delete("/{user_id}")
        def delete_user(user_id: int, db: Session = Depends(get_db)):
            return self.user_service.delete_user(db, user_id=user_id)

        @router.put("/{user_id}", response_model=UserRead)
        def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
            return self.user_service.update_user(db, user_id=user_id, user_update=user_update)


        # @router.post("/users/{user_id}/items/", response_model=schemas.Item)
        # def create_item_for_user(
        #     user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
        # ):
        #     return crud.create_user_item(db=db, item=item, user_id=user_id)
