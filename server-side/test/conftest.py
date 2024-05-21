import multiprocessing
import os
import queue
import shutil
from datetime import datetime
from multiprocessing import Queue

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.src.database import Base
from app.src.dependencies import get_db
from app.src.ml import WorkerMLInference
from app.src.models import Accident, Source, Threshold, Recipient, User
from app.src.models.enums import AccidentType, SourceStatus
from app.src.models.enums import SourceType
from app.src.schemas import UserCreate
from app.src.stream import WorkerStreamReader
from app.src.utilities import delete_file

load_dotenv()

# Create a SQLAlchemy engine
engine = create_engine(
    os.getenv('TEST_DB_URI'),
)

# Create a sessionmaker to manage sessions
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables in the database
Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

manager = multiprocessing.Manager()

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


@pytest.fixture(autouse=True)
def authenticated_user_data(test_client, db_session, user_data):
    response = test_client.post('/api/auth/login', data={'username': user_data.username,
                                                         'password': user_data.password})
    response_json = response.json()
    return user_data, response_json['access_token']


@pytest.fixture(autouse=True)
def user_data(db_session):
    username = password = 'testuser'
    password_hash = pwd_context.hash(password)
    user = User(username=username, password_hash=password_hash)
    db_session.add(user)
    db_session.commit()

    return UserCreate(username=username, password=password)



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


@pytest.fixture()
def threshold_data():
    return Threshold()


@pytest.fixture()
def recipient_data():
    return Recipient(email='mail1@mail.com')


@pytest.fixture()
def recipients_data():
    return [
        Recipient(email='mail1@mail.com'),
        Recipient(email='mail2@mail.com'),
        Recipient(email='mail3@mail.com'),
    ]


@pytest.fixture()
def uploaded_video_source(test_client, db_session, authenticated_user_data):
    video_file_name = 'test/static/video1.mp4'
    with open(video_file_name, 'rb') as f:
        response = test_client.post('/api/media', data={'title': 'VideoSource',
                                                        'description': 'VideoSource description',
                                                        'source_type': SourceType.VIDEO.value},
                                    files={'video_file': (video_file_name, f, 'video/mp4')},
                                    headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
    source_id = response.json()['id']
    source = db_session.query(Source).first()
    yield source

    # Cleanup
    sources = db_session.query(Source).all()
    for s in sources:
        delete_file(s.file_path)


@pytest.fixture()
def uploaded_stream_source(test_client, db_session, authenticated_user_data):
    stream_url = 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'
    response = test_client.post('/api/media', data={'title': 'StreamSource',
                                                    'description': 'StreamSource description',
                                                    'source_type': SourceType.STREAM.value,
                                                    'stream_url': stream_url},
                                headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
    return db_session.query(Source).first()


@pytest.fixture()
def uploaded_video_source_status_processing(test_client, db_session, authenticated_user_data):
    video_file_name = 'test/static/video1.mp4'
    with open(video_file_name, 'rb') as f:
        response = test_client.post('/api/media', data={'title': 'VideoSource',
                                                        'description': 'VideoSource description',
                                                        'source_type': SourceType.VIDEO.value},
                                    files={'video_file': (video_file_name, f, 'video/mp4')},
                                    headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
    source_json = response.json()
    source_id = source_json['id']
    response = test_client.get(f'/api/media/source/inference/{source_id}',
                               headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
    yield source_json

    # Cleanup
    # test_client.put(f'/api/media/source/stream/{source_id}')

@pytest.fixture()
def uploaded_stream_source_status_processing(test_client, db_session, authenticated_user_data):
    stream_url = 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'
    response = test_client.post('/api/media', data={'title': 'StreamSource',
                                                    'description': 'StreamSource description',
                                                    'source_type': SourceType.STREAM.value,
                                                    'stream_url': stream_url},
                                headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
    source_json = response.json()
    response = test_client.get(f'/api/media/source/inference/{source_json["id"]}', headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
    return source_json

@pytest.fixture()
def uploaded_video_source_with_accidents(test_client, db_session, accidents_data, authenticated_user_data):
    video_file_name = 'test/static/video1.mp4'
    with open(video_file_name, 'rb') as f:
        response = test_client.post('/api/media', data={'title': 'VideoSource',
                                                        'description': 'VideoSource description',
                                                        'source_type': SourceType.VIDEO.value},
                                    files={'video_file': (video_file_name, f, 'video/mp4')},
                                    headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
    source_id = response.json()['id']
    for a in accidents_data:
        a.source_id = source_id
        db_session.add(a)
    db_session.commit()
    return response.json()

@pytest.fixture()
def uploaded_stream_source_with_accidents(test_client, db_session, accidents_data, authenticated_user_data):
    stream_url = 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'
    response = test_client.post('/api/media', data={'title': 'StreamSource',
                                                    'description': 'StreamSource description',
                                                    'source_type': SourceType.STREAM.value,
                                                    'stream_url': stream_url},
                                headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
    source_id = response.json()['id']
    for a in accidents_data:
        a.source_id = source_id
        db_session.add(a)
    db_session.commit()
    return response.json()


@pytest.fixture()
def mocked_stream_reader():
    output_q = Queue(maxsize=100)
    shared_sources_dict = manager.dict()

    def on_done(data):
        try:
            output_q.put(data, block=False)
        except queue.Full:
            print(f'Output queue is full! Element not added.')
            return

    stream_reader = WorkerStreamReader(shared_sources_dict=shared_sources_dict,
                                       on_done=on_done)

    stream_reader.start()
    yield output_q, stream_reader

    stream_reader.stop()


@pytest.fixture()
def video_source_to_read():
    return 1, 'test/static/video1.mp4'


@pytest.fixture()
def mocked_ml_inference():
    input_q = Queue(maxsize=100)
    output_q = Queue(maxsize=100)
    batch_size = 30

    def on_done(data):
        try:
            output_q.put(data, block=False)
        except queue.Full:
            print(f'Output queue is full! Element not added.')
            return

    ml = WorkerMLInference(on_done=on_done, batch_size=batch_size)
    ml.start()
    yield batch_size, input_q, output_q, ml

    ml.stop()
