import os

from flask import current_app, request, session
from config import TestingConfig, Config

from firebase_admin import auth, firestore

import bookshelf
from bookshelf import create_app
from bookshelf.auth.forms import RegisterForm

def test_app_config(app):
    assert app.config.get('GOOGLE_APPLICATION_CREDENTIALS') == './keys/bookshelf-test-firebase-api.json'
    assert app.config.get('TESTING') == True

def test_hello(client):
    response = client.get('/hello')
    assert response.data == b'Hello bookshelf'

# Test Auth Routes
def test_login(client, login_json_data):
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

    
    # Response should be in JSON
    print('response:', rv)
    assert rv.status_code == 200
    assert rv.is_json
    assert 'firebase' in rv.headers['Set-Cookie']

def test_register(client, mock_register_data):
    """Takes Display Name, Email and Password to create an authenticated user
    
    Add user to firebase auth and firestore with the id == uid
    """
    rv = client.post('/register', data=mock_register_data)
    assert rv.status_code == 302

    # Get User info from auth and db to make sure it was added
    user = get_user_by_email(mock_register_data['email'])
    assert user is not None
    assert user_in_firestore(user.uid)

def get_user_by_email(email):
    try:
        user = auth.get_user_by_email(email)
    except Exception as e:
        raise e
    else:
        return user

def user_in_firestore(uid):
    db = firestore.client()
    doc_ref = db.document(f"users/{uid}")
    doc = doc_ref.get()
    return doc.exists

def test_session_logout(app, client):
    # clear firebase session cookie and clear flask session data
    # add mock user to session data:
    with client.session_transaction() as sess:
        sess['_user'] = 'User Data'
        sess.modified = True
    
    rv = client.post('/sessionLogout')
    assert rv.is_json
    assert 'Expires=Thu, 01-Jan-1970 00:00:00 GMT' in rv.headers['Set-Cookie']
    # TODO: assert the '_user' item is removed from session. I can see it is with
    #   the print statement in the route, but it doesn't seem to showing here
    #with app.app_context():
    #    print(session)
    #    assert '_user' in session


# Test Main Routes

