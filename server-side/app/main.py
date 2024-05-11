from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .src import root_router
from .src.database import engine, SessionLocal
from .src.models import Base, Threshold
from .src.settings import HOST, PORT

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This will create database tables
    Base.metadata.create_all(bind=engine)
    init_db()
    yield


def init_db():
    db: Session = SessionLocal()
    # Initialize sensitivity threshold
    threshold = db.query(Threshold).first()
    if threshold is None:
        threshold = Threshold()
        db.add(threshold)
        db.commit()
    db.close()


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
