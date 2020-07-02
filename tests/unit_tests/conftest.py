import pytest
import os
import json
from bookshelf import create_app
from config import TestingConfig
import requests
from firebase_admin import auth, firestore
import datetime
from flask import template_rendered
TEST_USER_EMAIL = "test_user@email.com"
TEST_USER_PASSWORD = "123123"

@pytest.fixture()
def app():
    app = create_app()   
    app.config.from_object(TestingConfig)   
    yield app

    # delete firebase app instance?

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

@pytest.fixture
def mock_register_data():
    mock_register_data = {
        'display_name': 'Mock User',
        'email': 'mock_user@gmail.com',
        'password': '123123',
        'confirm_password': '123123'
    }

    yield mock_register_data

    # Clean Up auth and database
    print('cleaning up...')
    user = auth.get_user_by_email(mock_register_data['email'])
    print(user.uid)
    # Delete Auth User
    auth.delete_user(user.uid)

    # Delete User from firestore
    db = firestore.client()
    doc_ref = db.document(f"users/{user.uid}")
    doc_ref.delete()

@pytest.fixture
def mock_logged_in_user(login_json_data):
    """Provide client with firebase session cookie set"""
    id_token, uid = login_json_data.values()
    expires_in = datetime.timedelta(days=5)
    # Exchange idToken for session cookie
    session_cookie = auth.create_session_cookie(id_token, expires_in)
    return {'session_cookie': session_cookie, 'uid': uid}

@pytest.fixture
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

@pytest.fixture
def mock_review_data(login_json_data):
    mock_review_data = {
    'rating': '3',
    'review_title': 'Test Review Title',
    'review_content': 'Test Review Content',
    'date_started': '06/01/2020',
    'date_finished': '06/15/2020'
    }

    book_id = 'CGVDDwAAQBAJ'

    yield book_id, mock_review_data

    # Delete Review document when finished
    db = firestore.client()
    print(f"users\{login_json_data['uid']}\books\{book_id}")
    doc_ref = db.collection("users").document("caEzKF0FEuaiU0QPuzPiNqtiVsp2").collection("books").document("CGVDDwAAQBAJ")
    doc_ref.delete()

@pytest.fixture
def mock_reading_data():
    mock_reading_data = {"bookId": "81HYDwAAQBAJ"}

    yield mock_reading_data

    # Delete Review document when finished
    db = firestore.client()
    doc_ref = db.collection("users").document("caEzKF0FEuaiU0QPuzPiNqtiVsp2").collection("books").document("81HYDwAAQBAJ")
    doc_ref.delete()

