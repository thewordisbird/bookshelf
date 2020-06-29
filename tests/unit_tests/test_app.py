import os
from bookshelf import create_app
from flask import current_app, request
from config import TestingConfig, Config
import bookshelf

def test_app_config(app):
    assert app.config.get('GOOGLE_APPLICATION_CREDENTIALS') == './keys/bookshelf-test-firebase-api.json'
    assert app.config.get('TESTING') == True

def test_hello(client):
    response = client.get('/hello')
    assert response.data == b'Hello bookshelf'

# Test Auth Routes
def test_login(app, client, login_json_data, monkeypatch):
    """Take ID Token and conver to session cookie.

    For testing purposes the ID token is obtained using the Firebase
    REST API. In Practice the ID token is passed from the js sdk on the 
    front end
    """
    
    rv = client.post('/login', json = login_json_data)
    #print(login_json_data)
    # Request should be in JSON
    print('request:', request)
    assert request.is_json
    assert request.get_json() == login_json_data

    # Monkeypatch create_session_cookie and set a mock session cookie
    def mock_create_session_cookie(*args, **kwargs):
        print('in mock')
        return 'mt_mock_session_cookie'

    monkeypatch.setattr(bookshelf.firebase_auth, 'create_session_cookie', mock_create_session_cookie)
    # Response should be in JSON
    print('response:', rv)
    assert rv.status_code == 200
    assert rv.is_json
    #assert rv.get_
    
