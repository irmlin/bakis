from fastapi import APIRouter

from .controllers import SourceController, AccidentController, SettingsController, AuthController

root_router = APIRouter(prefix="/api")
root_router.include_router(SourceController().router)
root_router.include_router(AccidentController().router)
root_router.include_router(SettingsController().router)
root_router.include_router(AuthController().router)

@root_router.get("/", tags=['health'])
async def health_check():
    return {"msg": "server up and running"}
