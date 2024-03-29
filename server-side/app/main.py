from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from src.settings import HOST, PORT
from contextlib import asynccontextmanager
import os
# from src.controllers import stream_router
from src.settings import HOST, PORT
from src.database import engine
from src.models import Base
from src import root_router

from fastapi.middleware.cors import CORSMiddleware




@asynccontextmanager
async def lifespan(app: FastAPI):
    # This will create database tables
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

# Allow requests from http://localhost:3000
# Good for developement stage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(root_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, log_level="info", reload=True)
