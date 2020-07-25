import os
import json
import requests
import pytest
import datetime
import firebase_admin
from firebase_admin import auth, firestore
from flask import template_rendered
from bookshelf import create_app
from bookshelf.firebase_wrapper import Firebase
from bookshelf.secrets_wrapper import access_secret_version

@pytest.fixture
def app():
    app = create_app("testing")
    return app

@pytest.fixture(scope="function")
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

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

def sign_in_with_email_and_password(email, password, web_api_key):
    endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={web_api_key}"
    headers = {"content-type": "application/json; charset=UTF-8"}
    data = json.dumps({"email": email, "password": password, "returnSecureToken": True})
    request_object = requests.post(endpoint, headers=headers, data=data)
    #raise_detailed_error(request_object)
    return request_object.json()


# Fixtures for auth routes testing
@pytest.fixture(scope="function")
def mock_login_data(config):
    
    # Create authenticated user in firebase
    user = {
        "display_name": "Test User",
        "email": "test_user@email.com",
        "password": "123123"
    }

    auth_user = auth.create_user(**user)
    

    # Add user to firestore
    db = firestore.client()
    doc_ref = db.document(f"users/{auth_user.uid}")
    doc = doc_ref.set(user)

    # Log user in using REST API. The user is logged in in the front end
    # with the js sdk, but the REST API will give us the information needed
    # to pass to the login funciton in flask
    firebase_resp = sign_in_with_email_and_password(user['email'], user['password'], \
        config.get('WEB_API_KEY'))

    login_json_data = {'idToken': firebase_resp['idToken'], 'uid': firebase_resp['localId']}
    
    yield login_json_data

    # Clean up
    auth.delete_user(auth_user.uid)

    doc_ref.delete()


# Fixtures for main routes testing
class AppUser:
    
    BOOKS = [
        {
            "authors": [
                "Delia Owens"
            ],
            "bid": "CGVDDwAAQBAJ",
            "cover_url": "https://books.google.com/books/content?id=CGVDDwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&imgtk=AFLRE701IBUI7BcmMLW2w7fEqpgCjYybdpj06YVocF1dP-SUZzZy46SDetTnF70P7FP-rc6BEV2ljs3gxEtPW2udRfpc4PZD7K8_pcNAYZ_AWh4vxXqHBXSmopoA6Nu2EWJMbhY5dfRv&source=gbs_api",
            "date_finished": datetime.datetime(2020, 7, 1),
            "date_rated": datetime.datetime(2020, 7, 1),
            "date_started": datetime.datetime(2020, 6, 1),
            "last_updated": datetime.datetime(2020, 7, 1),
            "rating": 5,
            "review_content": "Wonderful Book",
            "review_title": "5/5 Great Read!",
            "title": "Where The Crawdads Sing"
        },
        {
            "authors": [
                "Amor Towles"
            ],
            "bid": "-9CLDwAAQBAJ",
            "cover_url": "https://books.google.com/books/content?id=-9CLDwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&imgtk=AFLRE71k66HwjTniKF8NjabzC_nnmFNz52dVxUdAevbkN0MlMpyKou9dbJk0e9F0jPUdYxaFay5GbU_puhmSgkPf4bbyWo8mo7k5mUXvHBS3c8f5MG-PsuYwAG8Pu94ePEnp8V-AUrt9&source=gbs_api",
            "date_started": datetime.datetime(2020, 7, 1),
            "last_updated": datetime.datetime(2020, 7, 1),
            "rating": 5,
            "review_content": "Wonderful Book",
            "review_title": "5/5 Great Read!",
            "title": "A Gentleman in Moscow"
        }
    ]

    def __init__(self, display_name, email, password):
        self.display_name = display_name
        self.email = email
        self.password = password
        self.uid = None
        self.id_token = None
        self.session_cookie = None

    def init_app_user(self, web_api_key):
        self.create_firebase_user()
        self.add_books()
        self.login_app_user(web_api_key)
        self.get_session_cookie()
        
    def create_firebase_user(self):
        """Create Firebase authenticated user and add to firestore."""
        try:
            auth_user = auth.create_user(email=self.email, \
                display_name=self.display_name, password=self.password)
        except Exception as e:
            raise e
        else:  
            data = {
                "display_name": self.display_name,
                "email": self.email,
                "created": datetime.datetime.now(),
                "last_updated": datetime.datetime.now()
            }      
            db = firestore.client()
            doc_ref = db.document(f"users/{auth_user.uid}")
            doc = doc_ref.set(data)

            self.uid = auth_user.uid

    def add_books(self):
        db = firestore.client()
        for book in self.BOOKS:
            book['display_name'] = self.display_name
            book['uid'] = self.uid
            doc_ref = db.document(f"users/{self.uid}/books/{book['bid']}")
            doc_ref.set(book)

    def login_app_user(self, web_api_key):
        try:
            firebase_resp = sign_in_with_email_and_password(self.email, \
                self.password, web_api_key)
        except Exception as e:
            raise e
        else:
            self.id_token = firebase_resp['idToken']
    
    def get_session_cookie(self):
        try:
            session_cookie = auth.create_session_cookie(self.id_token, \
                expires_in=datetime.timedelta(days=5))
        except Exception as e: 
            raise e
        else:
            self.session_cookie = session_cookie
    
    def delete(self):
        auth.delete_user(self.uid)

        db = firestore.client()
        books_ref = db.collection(f"users/{self.uid}/books")
        books = books_ref.stream()
        for book in books:
            book._reference.delete()

        doc_ref = db.document(f"users/{self.uid}")
        doc_ref.delete()


@pytest.fixture(scope="module")
def app_user():
    """
    Application user with session id and pertinent profile information.

    In test, need to set cookie headers and session to mock logged in
    user state.
    """
    user_data = {
        "display_name": "Test User",
        "email": "test_user@email.com",
        "password": "123123"
    }

    user = AppUser(user_data["display_name"], user_data["email"], user_data["password"])
    web_api_key = access_secret_version(os.getenv("PROJECT_ID"), "WEB_API_KEY")
    user.init_app_user(web_api_key)

    yield user
    assert user.uid != None
    user.delete()