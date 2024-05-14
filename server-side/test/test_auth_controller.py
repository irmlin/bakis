# import pytest
#
# from app.src.models import Accident
# from app.src.utilities import file_exists
#
#
# class TestAuthController:
#
#     def test_login(self, test_client, user_data):
#         response = test_client.post('/api/auth/login', data={'username': user_data.username,
#                                                              'password': user_data.password})
#         response_json = response.json()
#         assert response.status_code == 200
#         assert len(response_json['access_token']) > 0 and response_json['token_type'] == 'bearer'
#
#     def test_login_bad_password(self, test_client, user_data):
#         response = test_client.post('/api/auth/login', data={'username': user_data.username,
#                                                              'password': 'badpassword'})
#         assert response.status_code == 401
#         assert response.json().get('access_token', None) is None
#
#     def test_login_user_does_not_exist(self, test_client):
#         response = test_client.post('/api/auth/login', data={'username': 'user',
#                                                              'password': 'password'})
#         assert response.status_code == 401
#         assert response.json().get('access_token', None) is None
#
#     def test_get_user(self, test_client, authenticated_user_data):
#         user_data, access_token = authenticated_user_data
#         response = test_client.get('/api/auth/user', headers={'Authorization': 'Bearer ' + access_token})
#         assert response.status_code == 200
#         assert user_data.username == response.json()['username']
