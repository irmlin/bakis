import time

import pytest
from fastapi import UploadFile

from app.src.models import Source
from app.src.models.enums import SourceType, source_status
from app.src.utilities import file_exists, delete_file
from app.src.models.enums import SourceStatus


class TestSourceController:
    def test_upload_source_video(self, db_session, test_client):
        video_file_name = 'test/static/video1.mp4'
        with open(video_file_name, 'rb') as f:
            response = test_client.post('/api/media', data={'title': 'VideoSource',
                                                            'description': 'VideoSource description',
                                                            'source_type': SourceType.VIDEO.value},
                                        files={'video_file': (video_file_name, f, 'video/mp4')})
        assert response.status_code == 200
        saved_id = response.json()['id']

        uploaded_source = db_session.query(Source).filter(Source.id == saved_id).first()
        assert uploaded_source.title == 'VideoSource'
        assert uploaded_source.description == 'VideoSource description'
        assert uploaded_source.source_type == SourceType.VIDEO
        assert file_exists(uploaded_source.file_path)
        assert uploaded_source.fps is not None
        assert uploaded_source.width is not None
        assert uploaded_source.height is not None
        assert uploaded_source.status == SourceStatus.NOT_PROCESSED

    def test_upload_source_video_when_video_not_provided(self, db_session, test_client):
        response = test_client.post('/api/media', data={'title': 'VideoSource',
                                                        'description': 'VideoSource description',
                                                        'source_type': SourceType.VIDEO.value})
        assert response.status_code == 400

    def test_upload_source_stream(self, db_session, test_client):
        stream_url = 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'
        response = test_client.post('/api/media', data={'title': 'StreamSource',
                                                        'description': 'StreamSource description',
                                                        'source_type': SourceType.STREAM.value,
                                                        'stream_url': stream_url})
        assert response.status_code == 200
        saved_id = response.json()['id']

        uploaded_source = db_session.query(Source).filter(Source.id == saved_id).first()
        assert uploaded_source.title == 'StreamSource'
        assert uploaded_source.description == 'StreamSource description'
        assert uploaded_source.source_type == SourceType.STREAM
        assert uploaded_source.fps is not None
        assert uploaded_source.width is not None
        assert uploaded_source.height is not None
        assert uploaded_source.status == SourceStatus.NOT_PROCESSED

    def test_upload_source_stream_when_stream_not_provided(self, db_session, test_client):
        response = test_client.post('/api/media', data={'title': 'StreamSource',
                                                        'description': 'StreamSource description',
                                                        'source_type': SourceType.VIDEO.value})
        assert response.status_code == 400

    def test_get_source(self, test_client, uploaded_video_source):
        response = test_client.get(f'/api/media/source/{uploaded_video_source.id}')
        assert response.status_code == 200
        assert response.json()['id'] == uploaded_video_source.id

    def test_get_source_when_source_does_not_exist(self, test_client):
        response = test_client.get('/api/media/source/1')
        assert response.status_code == 404

    def test_get_live_sources_when_there_are_none(self, test_client):
        response = test_client.get('/api/media/source/stream')
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_get_live_sources(self, test_client,
                              uploaded_video_source_status_processing,
                              uploaded_stream_source_status_processing):
        response = test_client.get('/api/media/source/stream')
        assert response.status_code == 200
        assert len(response.json()) == 2

        valid_ids = [uploaded_video_source_status_processing['id'], uploaded_stream_source_status_processing['id']]
        for live_source in response.json():
            assert live_source['status'] == SourceStatus.PROCESSING
            assert live_source['id'] in valid_ids
            valid_ids.remove(live_source['id'])

    def test_start_inference_task_for_video(self, test_client, db_session, uploaded_video_source):
        response = test_client.get(f'/api/media/source/inference/{uploaded_video_source.id}')
        assert response.status_code == 200
        assert db_session.query(Source).first().status == SourceStatus.PROCESSING

    def test_start_inference_task_for_stream(self, test_client, db_session, uploaded_stream_source):
        response = test_client.get(f'/api/media/source/inference/{uploaded_stream_source.id}')
        assert response.status_code == 200
        assert db_session.query(Source).first().status == SourceStatus.PROCESSING

    def test_start_inference_task_when_source_does_not_exist(self, test_client):
        response = test_client.get('/api/media/source/inference/1')
        assert response.status_code == 404

    def test_start_inference_task_when_video_file_does_not_exist(self, test_client, db_session, uploaded_video_source):
        delete_file(uploaded_video_source.file_path)
        response = test_client.get(f'/api/media/source/inference/{uploaded_video_source.id}')
        assert response.status_code == 404
        assert db_session.query(Source).first().status == SourceStatus.NOT_PROCESSED

    def test_start_inference_task_when_video_source_is_already_live(self, test_client,
                                                                    uploaded_video_source_status_processing):
        response = test_client.get(f'/api/media/source/inference/{uploaded_video_source_status_processing["id"]}')
        assert response.status_code == 404

    def test_start_inference_task_when_stream_source_is_already_live(self, test_client,
                                                                     uploaded_stream_source_status_processing):
        response = test_client.get(f'/api/media/source/inference/{uploaded_stream_source_status_processing["id"]}')
        assert response.status_code == 404

    def test_delete_source_video(self, test_client, uploaded_video_source):
        response = test_client.delete(f'/api/media/source/{uploaded_video_source.id}')
        assert response.status_code == 200
        assert not file_exists(uploaded_video_source.file_path)
        response = test_client.get(f'/api/media/source/{uploaded_video_source.id}')
        assert response.status_code == 404

    def test_delete_source_stream(self, test_client, uploaded_stream_source):
        response = test_client.delete(f'/api/media/source/{uploaded_stream_source.id}')
        assert response.status_code == 200
        response = test_client.get(f'/api/media/source/{uploaded_stream_source.id}')
        assert response.status_code == 404

    def test_delete_source_video_when_source_does_not_exist(self, test_client):
        response = test_client.delete('/api/media/source/1')
        assert response.status_code == 404

    def test_delete_source_video_when_source_still_processing(self, test_client, db_session,
                                                              uploaded_video_source_status_processing):
        response = test_client.delete(f'/api/media/source/{uploaded_video_source_status_processing["id"]}')
        assert response.status_code == 409
        source = db_session.query(Source).filter(Source.id == uploaded_video_source_status_processing['id']).first()
        assert file_exists(source.file_path)

    def test_delete_source_stream_when_source_still_processing(self, test_client,
                                                               uploaded_stream_source_status_processing):
        response = test_client.delete(f'/api/media/source/{uploaded_stream_source_status_processing["id"]}')
        assert response.status_code == 409

    def test_delete_source_video_with_accidents(self, test_client, uploaded_video_source_with_accidents):
        source_id = uploaded_video_source_with_accidents['id']
        response = test_client.get('/api/accident')
        assert response.status_code == 200
        assert len(response.json()) == 3

        response = test_client.delete(f'/api/media/source/{source_id}')
        assert response.status_code == 200

        response = test_client.get('/api/accident')
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_delete_source_stream_with_accidents(self, test_client, uploaded_stream_source_with_accidents):
        source_id = uploaded_stream_source_with_accidents['id']
        response = test_client.get('/api/accident')
        assert response.status_code == 200
        assert len(response.json()) == 3

        response = test_client.delete(f'/api/media/source/{source_id}')
        assert response.status_code == 200

        response = test_client.get('/api/accident')
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_terminate_live_stream_when_source_video(self, test_client, db_session,
                                                     uploaded_stream_source_status_processing):
        source_id = uploaded_stream_source_status_processing['id']
        response = test_client.put(f'/api/media/source/stream/{source_id}')
        assert response.status_code == 200

        source = db_session.query(Source).filter(Source.id == source_id).first()
        assert source.status == SourceStatus.TERMINATED

    def test_terminate_live_stream_when_source_does_not_exist(self, test_client):
        response = test_client.put('/api/media/source/stream/1')
        assert response.status_code == 404

    def test_terminate_live_stream_when_source_was_not_live(self, test_client, db_session,
                                                            uploaded_stream_source):
        source_id = uploaded_stream_source.id
        response = test_client.put(f'/api/media/source/stream/{source_id}')
        assert response.status_code == 400

    # def test_stream_source(self, test_client, uploaded_stream_source_status_processing):
    #     source_id = uploaded_stream_source_status_processing['id']
    #     counter = 0
    #     max_counter = 10
    #     with test_client.websocket_connect(f"/api/media/source/stream/{source_id}") as websocket:
    #         while counter < max_counter:
    #             data = websocket.receive_bytes()
    #             assert len(data) > 0
    #             counter += 1
