from fastapi import APIRouter

from ..services import SettingsService


class SettingsController:

    def __init__(self):
        self.router = APIRouter(tags=["settings"], prefix="/settings")
        self.settings_service = SettingsService()

        self.__init_routes(router=self.router)

    def __init_routes(self, router):
        pass
