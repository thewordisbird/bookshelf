import os
import pytest
import firebase_admin
import json
from firebase_admin import auth
from bookshelf.firebase_wrapper import Firebase

def test_construct_firebase():
    firebase = Firebase()
    assert type(firebase).__name__ == "Firebase"

def test_init_app():
    firebase = Firebase()
    
    google_application_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    assert google_application_credentials != None
    web_api_key = "Test API KEY"

    assert firebase_admin._apps.get('[DEFAULT]', None) == None
    
    firebase.init_app(google_application_credentials, web_api_key)

    assert firebase.google_application_credentials == google_application_credentials
    assert firebase.web_api_key == web_api_key

    assert firebase_admin._apps.get('[DEFAULT]', None) != None

def test_construct_auth(firebase):
    assert type(firebase.auth()).__name__ == "Auth"

def test_construct_firestore(firebase):
    assert type(firebase.firestore()).__name__ == "Firestore"

# Tests for Auth Class
def create_session_cookie(firebase):
    pass

def test_create_new_user_with_email_password_display_name(firebase):
    firebase_auth = firebase.auth()

    user = {
        "email": "test_user@email.com",
        "password": "123123",
        "display_name": "Test User"
    }
    assert firebase_admin._apps.get('[DEFAULT]', None) != None
    auth_user = firebase_auth.create_new_user_with_email_password_display_name(**user)

    assert auth_user.email == user.get('email')

    try:
        auth.delete_user(auth_user.uid)
    except:
        pass


def test_get_user(firebase):
    firebase_auth = firebase.auth()

    user = {
        "email": "test_user@email.com",
        "password": "123123",
        "display_name": "Test User"
    }

    auth_user = firebase_auth.create_new_user_with_email_password_display_name(**user)

    uid = auth_user.uid

    response_user = firebase_auth.get_user(uid)

    assert response_user.email == user['email']
    assert response_user.display_name == user['display_name']

    try:
        auth.delete_user(auth_user.uid)
    except:
        pass


def test_update_user(firebase):
    firebase_auth = firebase.auth()

    user = {
        "email": "test_user@email.com",
        "password": "123123",
        "display_name": "Test User"
    }

    auth_user = firebase_auth.create_new_user_with_email_password_display_name(**user)

    updated_auth_user = firebase_auth.update_user(auth_user.uid, {'display_name': 'User Test'})

    assert updated_auth_user.display_name == 'User Test'

    try:
        auth.delete_user(auth_user.uid)
    except:
        pass


# Tests for Firestore Class
def test_crud(firebase):
    # Tests:
    #   firestore.set_documnet
    #   firestore.get_document
    #   firestore.update_document
    #   firestore.delete_documents
    firebase_firestore = firebase.firestore()

    doc_path = "users"
    
    doc_id = "abc123"

    data = {
        "name": "Jane Doe",
        "email": "jane.doe@email.com"
    }

    firebase_firestore.set_document(f"{doc_path}/{doc_id}", data)

    db_data = firebase_firestore.get_document(f"{doc_path}/{doc_id}")

    assert db_data["name"] == data["name"]
    assert db_data["email"] == data["email"]

    update_data = {"name": "John Doe"}

    firebase_firestore.update_document(f"{doc_path}/{doc_id}", update_data)
    db_data = firebase_firestore.get_document(f"{doc_path}/{doc_id}")
    
    assert db_data["name"] == update_data["name"]
    assert db_data["email"] == data["email"]
    
    try:
        firebase_firestore.delete_document(f"{doc_path}/{doc_id}")
    except:
        pass

    assert firebase_firestore.get_document(f"{doc_path}/{doc_id}") == None


def test_collections(firebase):
    # Tests 
    #   firesote.set_documents_from_json
    #   firesote.get_collection
    firebase_firestore = firebase.firestore()

    base_dir = os.path.abspath(os.path.dirname(__file__))
    assert base_dir == "/usr/src/app/tests"
    json_path = os.path.join(base_dir, "sample_collection.json")
    assert json_path == "/usr/src/app/tests/sample_collection.json"

    firebase_firestore.set_documents_from_json("users", json_path)

    firestore_users = firebase_firestore.get_collection("users")

    assert len(firestore_users) == 5

    with open(json_path) as f:
        json_data = json.load(f)

    for item in json_data:
        firebase_firestore.delete_document(f"users/{item['_id']}")


def test_get_collection_group(firebase):
    # Need to automate build of firestore with nested collections to test
    pass
