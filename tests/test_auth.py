import json
# import requests# 
from firebase_admin import auth, firestore
from flask import url_for, request, session

def test_hello(client, firebase):
    assert client.get(url_for('hello')).status_code == 200

def test_register(client):
    assert client.get(url_for('auth.register')).status_code == 200

    register_data = {
        "display_name": "Test User",
        "email": "test_user@email.com",
        "password": "123123",
        "confirm_password": "123123"
    }

    resp = client.post(url_for('auth.register'), data = register_data)
    assert resp.status_code == 302

    # Check for registered user in firebase auth
    auth_user = auth.get_user_by_email(register_data["email"])
    assert auth_user != None

    db = firestore.client()
    doc_ref = db.document(f"users/{auth_user.uid}")
    db_user = doc_ref.get()
    assert db_user.exists
    
    # Clean up
    auth.delete_user(auth_user.uid)
    doc_ref.delete()


def test_login(client, mock_login_data):
    assert client.get(url_for('auth.login')).status_code == 200
    
    login_resp = client.post(url_for('auth.login'), json = mock_login_data)
    # Request should be JSON
    assert request.is_json
    assert request.get_json() == mock_login_data

    # Response should be JSON
    assert login_resp.status_code == 200
    assert login_resp.is_json
    assert 'firebase' in login_resp.headers['Set-Cookie']

    # Logout User
    logout_resp = client.post(url_for('auth.session_logout'))
    assert logout_resp.is_json
    assert 'Expires=Thu, 01-Jan-1970 00:00:00 GMT' in logout_resp.headers['Set-Cookie']
    assert session.get('_user', None) == None


def test_reset_password(client):
    pass

