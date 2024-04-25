from fastapi import APIRouter
from .controllers import UserController, MediaController, AccidentController


root_router = APIRouter(prefix="/api")
root_router.include_router(UserController().router)
root_router.include_router(MediaController().router)
root_router.include_router(AccidentController().router)

@root_router.get("/", tags=['health'])
async def health_check():
    return {"msg": "server up and running"}