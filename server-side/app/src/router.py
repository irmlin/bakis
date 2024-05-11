from fastapi import APIRouter
from .controllers import UserController, SourceController, AccidentController, SettingsController


root_router = APIRouter(prefix="/api")
root_router.include_router(UserController().router)
root_router.include_router(SourceController().router)
root_router.include_router(AccidentController().router)
root_router.include_router(SettingsController().router)

@root_router.get("/", tags=['health'])
async def health_check():
    return {"msg": "server up and running"}
