from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

# from src import root_router
from .src.database import engine, SessionLocal
from .src.models import Base, Threshold
from .src.settings import HOST, PORT
from .src.controllers import SourceController, AccidentController, SettingsController, AuthController


def init_db():
    db: Session = SessionLocal()
    # Initialize sensitivity threshold
    threshold = db.query(Threshold).first()
    if threshold is None:
        threshold = Threshold()
        db.add(threshold)
        db.commit()
    db.close()


root_router = APIRouter(prefix="/api")
source_controller = SourceController()
root_router.include_router(source_controller.router)
root_router.include_router(AccidentController().router)
root_router.include_router(SettingsController().router)
root_router.include_router(AuthController().router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This will create database tables
    Base.metadata.create_all(bind=engine)
    init_db()

    source_controller.source_service.start_workers()
    yield
    source_controller.source_service.stop_workers()


app = FastAPI(lifespan=lifespan)


# Allow requests from http://localhost:3000
# Good for development stage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


app.include_router(root_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, log_level="info", reload=False)
