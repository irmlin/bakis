import pytest

from app.src.models import Accident
from app.src.utilities import file_exists


class TestAccidentController:
    def test_get_accidents(self, db_session, test_client, accidents_data, source_data):
        db_session.add(source_data)
        db_session.commit()
        db_session.refresh(source_data)
        for accident in accidents_data:
            accident.source_id = source_data.id
            db_session.add(accident)
        db_session.commit()

        response = test_client.get('/api/accident')
        response_json = response.json()
        assert response.status_code == 200
        assert len(response_json) == 3

    def test_get_accidents_filtered_by_datetime_from(self, db_session, test_client, accidents_data, source_data,
                                                     datetime_from):
        db_session.add(source_data)
        db_session.commit()
        db_session.refresh(source_data)
        for accident in accidents_data:
            accident.source_id = source_data.id
            db_session.add(accident)
        db_session.commit()

        response = test_client.get('/api/accident', params={'datetime_from': datetime_from})
        response_json = response.json()
        assert response.status_code == 200
        assert len(response_json) == 2

    def test_get_accidents_filtered_by_datetime_to(self, db_session, test_client, accidents_data, source_data,
                                                   datetime_to):
        db_session.add(source_data)
        db_session.commit()
        db_session.refresh(source_data)
        for accident in accidents_data:
            accident.source_id = source_data.id
            db_session.add(accident)
        db_session.commit()

        response = test_client.get('/api/accident', params={'datetime_to': datetime_to})
        response_json = response.json()
        assert response.status_code == 200
        assert len(response_json) == 2

    def test_get_accidents_filtered_by_datetime_from_to(self, db_session, test_client, accidents_data, source_data,
                                                        datetime_from, datetime_to):
        db_session.add(source_data)
        db_session.commit()
        db_session.refresh(source_data)
        for accident in accidents_data:
            accident.source_id = source_data.id
            db_session.add(accident)
        db_session.commit()

        response = test_client.get('/api/accident', params={'datetime_from': datetime_from, 'datetime_to': datetime_to})
        response_json = response.json()
        assert response.status_code == 200
        assert len(response_json) == 1

    def test_get_accidents_filtered_when_datetime_from_invalid(self, db_session, test_client, accidents_data,
                                                               source_data):
        db_session.add(source_data)
        db_session.commit()
        db_session.refresh(source_data)
        for accident in accidents_data:
            accident.source_id = source_data.id
            db_session.add(accident)
        db_session.commit()

        response = test_client.get('/api/accident', params={'datetime_from': '2024--1-15 , 14:00:55'})
        assert response.status_code == 422

    def test_get_accidents_filtered_when_datetime_to_invalid(self, db_session, test_client, accidents_data,
                                                             source_data):
        db_session.add(source_data)
        db_session.commit()
        db_session.refresh(source_data)
        for accident in accidents_data:
            accident.source_id = source_data.id
            db_session.add(accident)
        db_session.commit()

        response = test_client.get('/api/accident', params={'datetime_to': '2024--1-15 , 14:00:55'})
        assert response.status_code == 422

    def test_get_accidents_filtered_by_existing_source_id(self, db_session, test_client, accidents_data, source_data):
        db_session.add(source_data)
        db_session.commit()
        db_session.refresh(source_data)

        for accident in accidents_data:
            accident.source_id = source_data.id
            db_session.add(accident)
        db_session.commit()

        response = test_client.get('/api/accident', params={'source_ids': [source_data.id]})
        response_json = response.json()
        assert response.status_code == 200
        assert len(response_json) == 3

    def test_get_accidents_filtered_by_non_existent_source_id(self, db_session, test_client, accidents_data,
                                                              source_data):
        db_session.add(source_data)
        db_session.commit()
        db_session.refresh(source_data)

        for accident in accidents_data:
            accident.source_id = source_data.id
            db_session.add(accident)
        db_session.commit()

        response = test_client.get('/api/accident', params={'source_ids': [source_data.id + 1]})
        response_json = response.json()
        assert response.status_code == 200
        assert len(response_json) == 0

    def test_get_accident_image(self, db_session, test_client, accident_data, source_data):
        db_session.add(source_data)
        db_session.commit()
        db_session.refresh(source_data)

        accident_data.source_id = source_data.id
        db_session.add(accident_data)
        db_session.commit()
        db_session.refresh(accident_data)

        response = test_client.get(f'/api/accident/image/{accident_data.id}')
        assert response.status_code == 200
        assert response.headers['content-type'] == 'image/jpeg'
        assert len(response.content) > 0
        assert int(response.headers['content-length']) == len(response.content)

    def test_get_accident_image_when_image_does_not_exist(self, db_session, test_client, accident_data, source_data):
        db_session.add(source_data)
        db_session.commit()
        db_session.refresh(source_data)

        accident_data.source_id = source_data.id
        accident_data.image_path = 'non_existent_image_path.jpg'
        db_session.add(accident_data)
        db_session.commit()
        db_session.refresh(accident_data)

        response = test_client.get(f'/api/accident/image/{accident_data.id}')
        assert response.status_code == 404

    def test_get_accident_image_when_accident_does_not_exist(self, test_client):
        response = test_client.get('/api/accident/image/1')
        assert response.status_code == 404

    def test_download_accident_video(self, db_session, test_client, accident_data, source_data):
        db_session.add(source_data)
        db_session.commit()
        db_session.refresh(source_data)

        accident_data.source_id = source_data.id
        db_session.add(accident_data)
        db_session.commit()
        db_session.refresh(accident_data)

        response = test_client.get(f'/api/accident/video/download/{accident_data.id}')

        assert response.status_code == 200
        assert response.headers['content-type'] == 'video/mp4'
        assert 'attachment' in response.headers['content-disposition']
        assert int(response.headers['content-length']) == len(response.content)

    def test_download_accident_video_when_video_does_not_exist(self, db_session, test_client, accident_data,
                                                               source_data):
        db_session.add(source_data)
        db_session.commit()
        db_session.refresh(source_data)

        accident_data.source_id = source_data.id
        accident_data.video_path = 'non_existent_video.mp4'
        db_session.add(accident_data)
        db_session.commit()
        db_session.refresh(accident_data)

        response = test_client.get(f'/api/accident/video/download/{accident_data.id}')

        assert response.status_code == 404

    def test_download_accident_video_when_accident_does_not_exist(self, test_client):
        response = test_client.get('/api/accident/video/download/1')
        assert response.status_code == 404

    def test_download_report_pdf(self, db_session, test_client, accidents_data, source_data):
        db_session.add(source_data)
        db_session.commit()
        db_session.refresh(source_data)

        for accident in accidents_data:
            accident.source_id = source_data.id
            db_session.add(accident)
        db_session.commit()

        response = test_client.get(f'/api/accident/report/pdf')

        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/pdf'
        assert 'attachment' in response.headers['content-disposition']
        assert int(response.headers['content-length']) == len(response.content)

    def test_download_report_pdf_when_no_accidents(self, db_session, test_client):
        response = test_client.get(f'/api/accident/report/pdf')

        assert response.status_code == 404

    def test_download_report_pdf_when_invalid_datetime_to_passed(self, db_session, test_client, accidents_data,
                                                                 source_data):
        db_session.add(source_data)
        db_session.commit()
        db_session.refresh(source_data)

        for accident in accidents_data:
            accident.source_id = source_data.id
            db_session.add(accident)
        db_session.commit()

        response = test_client.get(f'/api/accident/report/pdf', params={"datetime_to": "2024--1-15"})

        assert response.status_code == 422

    def test_download_report_excel(self, db_session, test_client, accidents_data, source_data):
        db_session.add(source_data)
        db_session.commit()
        db_session.refresh(source_data)

        for accident in accidents_data:
            accident.source_id = source_data.id
            db_session.add(accident)
        db_session.commit()

        response = test_client.get(f'/api/accident/report/excel')

        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        assert 'attachment' in response.headers['content-disposition']
        assert int(response.headers['content-length']) == len(response.content)

    def test_download_report_excel_when_no_accidents(self, db_session, test_client):
        response = test_client.get(f'/api/accident/report/excel')

        assert response.status_code == 404

    def test_download_report_excel_when_invalid_datetime_to_passed(self, db_session, test_client, accidents_data,
                                                                   source_data):
        db_session.add(source_data)
        db_session.commit()
        db_session.refresh(source_data)

        for accident in accidents_data:
            accident.source_id = source_data.id
            db_session.add(accident)
        db_session.commit()

        response = test_client.get(f'/api/accident/report/excel', params={"datetime_to": "2024--1-15"})

        assert response.status_code == 422

    def test_delete_accident(self, db_session, test_client, accident_data, source_data, authenticated_user_data):
        db_session.add(source_data)
        db_session.commit()
        db_session.refresh(source_data)

        accident_data.source_id = source_data.id
        db_session.add(accident_data)
        db_session.commit()
        db_session.refresh(accident_data)

        response = test_client.delete(f'/api/accident/{accident_data.id}', headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})

        assert response.status_code == 200
        assert db_session.query(Accident).filter_by(id=accident_data.id).count() == 0
        assert not file_exists(accident_data.video_path)
        assert not file_exists(accident_data.image_path)

    def test_delete_accident_when_accident_does_not_exist(self, test_client, authenticated_user_data):
        response = test_client.delete('/api/accident/1', headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
        assert response.status_code == 404