import os
import shutil
from datetime import datetime

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.src.database import Base
from app.src.dependencies import get_db
from app.src.models import Accident, Source
from app.src.models.enums import AccidentType, SourceStatus
from app.src.models.enums import SourceType

load_dotenv()


# Create a SQLAlchemy engine
engine = create_engine(
    os.getenv('TEST_DB_URI'),
)

# Create a sessionmaker to manage sessions
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables in the database
Base.metadata.create_all(bind=engine)



@pytest.fixture(scope="function")
def db_session():
    """Create a new database session with a rollback at the end of the test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def test_client(db_session):
    """Create a test client that uses the override_get_db fixture to return a session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def serve_media_files():
    backup_folder = 'test/static/backup'
    backup_media_files = os.listdir(backup_folder)
    assert 'accident1.jpg' in backup_media_files, f'Missing accident1.jpg in {backup_folder}'
    assert 'accident1.mp4' in backup_media_files, f'Missing accident1.mp4 in {backup_folder}'
    assert 'video1.mp4' in backup_media_files, f'Missing video1.mp4 in {backup_folder}'

    static_folder = 'test/static'
    static_media_files = os.listdir(static_folder)
    for media_file in backup_media_files:
        if media_file not in static_media_files:
            shutil.copy(os.path.join(backup_folder, media_file), static_folder)

    yield


@pytest.fixture()
def accident_data():
    video_path = 'test/static/accident1.mp4'
    image_path = 'test/static/accident1.jpg'
    return Accident(type=AccidentType.CAR_CRASH, source_id=1, score=0.9,
                    created_at=datetime.strptime("2024-04-15 12:00:00", "%Y-%m-%d %H:%M:%S"),
                    image_path=image_path, video_path=video_path)


@pytest.fixture()
def accidents_data():
    video_path = 'test/static/accident1.mp4'
    image_path = 'test/static/accident1.jpg'
    return [
        Accident(type=AccidentType.CAR_CRASH, score=0.7,
                 created_at=datetime.strptime("2024-04-15 12:00:00", "%Y-%m-%d %H:%M:%S"),
                 image_path=image_path, video_path=video_path),
        Accident(type=AccidentType.CAR_CRASH, score=0.8,
                 created_at=datetime.strptime("2024-04-15 13:00:00", "%Y-%m-%d %H:%M:%S"),
                 image_path=image_path, video_path=video_path),
        Accident(type=AccidentType.CAR_CRASH, score=0.9,
                 created_at=datetime.strptime("2024-04-15 14:00:00", "%Y-%m-%d %H:%M:%S"),
                 image_path=image_path, video_path=video_path)
    ]

@pytest.fixture()
def datetime_from():
    return datetime.strptime("2024-04-15 12:30:00", "%Y-%m-%d %H:%M:%S")

@pytest.fixture()
def datetime_to():
    return datetime.strptime("2024-04-15 13:30:00", "%Y-%m-%d %H:%M:%S")

@pytest.fixture()
def source_data():
    file_path = 'test/static/accident1.mp4'
    return Source(title='Source1', description='Source1 description', file_path=file_path, created_at=datetime.utcnow(),
                  status=SourceStatus.NOT_PROCESSED, fps=25.05, height=352, width=640, source_type=SourceType.VIDEO)