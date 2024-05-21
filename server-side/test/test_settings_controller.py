import pytest

from app.src.models import Recipient


class TestSettingsController:
    def test_get_threshold(self, db_session, test_client, threshold_data, authenticated_user_data):
        db_session.add(threshold_data)
        db_session.commit()
        db_session.refresh(threshold_data)
        response = test_client.get('/api/settings/threshold', headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
        assert response.status_code == 200
        assert response.json()['car_crash_threshold'] == threshold_data.car_crash_threshold

    def test_get_threshold_when_does_not_exist(self, test_client, authenticated_user_data):
        response = test_client.get('/api/settings/threshold', headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
        assert response.status_code == 404

    def test_update_threshold(self, db_session, test_client, threshold_data, authenticated_user_data):
        db_session.add(threshold_data)
        db_session.commit()
        db_session.refresh(threshold_data)
        new_thr = 0.9
        response = test_client.put('/api/settings/threshold', data={'threshold': new_thr}, headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
        assert response.status_code == 200
        assert response.json()['car_crash_threshold'] == new_thr

    def test_update_threshold_when_threshold_invalid(self, db_session, test_client, threshold_data, authenticated_user_data):
        db_session.add(threshold_data)
        db_session.commit()
        db_session.refresh(threshold_data)
        new_thr = 1.1
        response = test_client.put('/api/settings/threshold', data={'threshold': new_thr}, headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
        assert response.status_code == 400

    def test_update_threshold_when_threshold_does_not_exist(self, test_client, authenticated_user_data):
        new_thr = 1.0
        response = test_client.put('/api/settings/threshold', data={'threshold': new_thr}, headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
        assert response.status_code == 404

    def test_get_recipients(self, db_session, test_client, recipients_data, authenticated_user_data):
        for r in recipients_data:
            db_session.add(r)
        db_session.commit()

        response = test_client.get('/api/settings/recipient', headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_get_recipients_when_no_recipients_exist(self, test_client, authenticated_user_data):
        response = test_client.get('/api/settings/recipient', headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_add_recipient(self, db_session, test_client, recipient_data, authenticated_user_data):
        response = test_client.post('/api/settings/recipient', data={'email': recipient_data.email}, headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
        assert response.status_code == 200
        assert response.json()['email'] == recipient_data.email

        response = test_client.get('/api/settings/recipient', headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_add_recipient_when_email_format_invalid(self, db_session, test_client, authenticated_user_data):
        response = test_client.post('/api/settings/recipient', data={'email': 'invalid_email@email@email.com@'}, headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
        assert response.status_code == 400

        response = test_client.get('/api/settings/recipient', headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_add_recipient_when_recipient_email_duplicate(self, db_session, test_client, recipient_data, authenticated_user_data):
        response = test_client.post('/api/settings/recipient', data={'email': recipient_data.email}, headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
        assert response.status_code == 200
        assert response.json()['email'] == recipient_data.email

        response = test_client.get('/api/settings/recipient', headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = test_client.post('/api/settings/recipient', data={'email': recipient_data.email}, headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
        assert response.status_code == 400

        response = test_client.get('/api/settings/recipient', headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_delete_recipient(self, db_session, test_client, recipient_data, authenticated_user_data):
        response = test_client.post('/api/settings/recipient', data={'email': recipient_data.email}, headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
        assert response.status_code == 200
        assert response.json()['email'] == recipient_data.email
        saved_id = response.json()['id']

        response = test_client.get('/api/settings/recipient', headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
        assert response.status_code == 200
        assert len(response.json()) == 1

        response = test_client.delete(f'/api/settings/recipient/{saved_id}', headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
        assert response.status_code == 200

        response = test_client.get('/api/settings/recipient', headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
        assert response.status_code == 200
        assert len(response.json()) == 0

        assert db_session.query(Recipient).filter_by(id=saved_id).count() == 0

    def test_delete_recipient_when_recipient_does_not_exist(self, test_client, authenticated_user_data):
        response = test_client.delete('/api/settings/recipient/1', headers={'Authorization': 'Bearer ' + authenticated_user_data[1]})
        assert response.status_code == 404