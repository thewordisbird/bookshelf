import os
import pytest
import firebase_admin
from bookshelf import create_app
from bookshelf.firebase_wrapper import Firebase
from bookshelf.secrets_wrapper import access_secret_version

@pytest.fixture
def app():
    app = create_app("testing")

    return app

# Fixtures for firebase_wrapper
@pytest.fixture(scope="function")
def firebase():
    if firebase_admin._apps:
        #print('deleting firebase app')
        firebase_admin.delete_app(firebase_admin._apps['[DEFAULT]'])

    google_application_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    web_api_key = access_secret_version(os.getenv("PROJECT_ID"), "WEB_API_KEY")

    firebase = Firebase()
    firebase.init_app(google_application_credentials, web_api_key)

    yield firebase

    # Delete firebase app instance
    firebase_admin.delete_app(firebase_admin._apps['[DEFAULT]'])