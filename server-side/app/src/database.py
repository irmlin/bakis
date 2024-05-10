from sqlalchemy import create_engine
from .settings import DB_URI
from sqlalchemy.orm import declarative_base, sessionmaker


engine = create_engine(DB_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
