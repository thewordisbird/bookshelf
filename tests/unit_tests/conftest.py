import pytest
import os
import json
from bookshelf import create_app
from config import TestingConfig
import requests

TEST_USER_EMAIL = "test_user@email.com"
TEST_USER_PASSWORD = "123123"

@pytest.fixture()
def app():
    app = create_app()   
    app.config.from_object(TestingConfig)   
    yield app

@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client
    
@pytest.fixture
def logged_in_user(client):
    pass

@pytest.fixture
def login_json_data():
    firebase_response = sign_in_with_email_and_password(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    json_data = {'idToken': firebase_response['idToken'], 'uid': firebase_response['localId']}
    return json_data
        


def sign_in_with_email_and_password(email, password):
    endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={os.environ.get('WEB_API_TEST_KEY')}"
    headers = {"content-type": "application/json; charset=UTF-8"}
    data = json.dumps({"email": email, "password": password, "returnSecureToken": True})
    request_object = requests.post(endpoint, headers=headers, data=data)
    raise_detailed_error(request_object)
    return request_object.json()

def raise_detailed_error(request_object):
    try:
        request_object.raise_for_status()
    except HTTPError as e:
        # raise detailed error message
        # TODO: Check if we get a { "error" : "Permission denied." } and handle automatically
        raise HTTPError(e, request_object.text)