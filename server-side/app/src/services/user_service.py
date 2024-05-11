# from fastapi import HTTPException
# from sqlalchemy.orm import Session
#
# from ..models import User
#
#
class UserService:

    def __init__(self):
        pass
#
#     def get_user_by_id(self, db: Session, user_id: int):
#         return db.query(User).filter(User.id == user_id).first()
#
#     def get_user_by_email(self, db: Session, email: str):
#         return db.query(User).filter(User.email == email).first()
#
#     def get_users(self, db: Session):
#         return db.query(User).all()
#
#     def get_user(self, db: Session, user_id: int):
#         db_user = self.get_user_by_id(db, user_id=user_id)
#         if db_user is None:
#             raise HTTPException(status_code=404, detail=f'User (id={user_id}) not found.')
#         return db_user
#
#     def create_user(self, db: Session, user_create: UserCreate):
#         db_user = self.get_user_by_email(db, email=user_create.email)
#         if db_user:
#             raise HTTPException(status_code=400, detail=f'Email ({db_user.email}) already registered.')
#         fake_hashed_password = user_create.password + "notreallyhashed"
#         db_user = User(email=user_create.email, password_hash=fake_hashed_password,
#                        first_name=user_create.first_name, last_name=user_create.last_name)
#         db.add(db_user)
#         db.commit()
#         db.refresh(db_user)
#         return db_user
#
#     def delete_user(self, db: Session, user_id: int):
#         user = self.get_user_by_id(db, user_id=user_id)
#         if user is None:
#             raise HTTPException(status_code=404, detail=f'User (id={user_id}) not found.')
#         db.delete(user)
#         db.commit()
#         return {'message': f'User (id={user_id}) had been deleted successfully.'}
#
#     def update_user(self, db: Session, user_id: int, user_update: UserUpdate):
#         db_user = self.get_user_by_id(db, user_id=user_id)
#         if db_user is None:
#             raise HTTPException(status_code=404, detail=f'User (id={user_id}) not found.')
#         db_user.email = user_update.email
#         db_user.password_hash = user_update.password + "notreallyhashed"
#         db.commit()
#         db.refresh(db_user)
#         return db_user
