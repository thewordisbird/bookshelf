import os
import datetime
import json
import pytest
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
def test_index_logged_in(client, mock_logged_in_user, captured_templates):
    
    
    # Set mock request header
    session_cookie, uid = mock_logged_in_user.values()
    client.set_cookie('localhost', 'firebase', session_cookie)

    rv = client.get('/')
    
    assert len(captured_templates) != 0
    template, context = captured_templates[0]

    assert template.name == 'index.html'
    assert context['title'] == 'bookshelf | home'
    # The test database is pre-populated with 2 books.
    assert len(context['books']) == 2

def test_profile_logged_in(client, mock_logged_in_user, captured_templates):
    session_cookie, uid = mock_logged_in_user.values()
    
    # Set mock request header
    client.set_cookie('localhost', 'firebase', session_cookie)
    
    # Add user to mock flask session
    with client.session_transaction() as sess:
        sess['_user'] = {
            'display_name': 'Test User',
            'uid': uid
        }
        sess.modified = True
    
    rv = client.get(f'/profile/{uid}')
    
    assert len(captured_templates) != 0
    template, context = captured_templates[0]

    assert template.name == 'profile.html'
    assert context['title'] == 'bookshelf | Test User'
    # The database is pre-populated with one user: Test User
    # who has 2 books:
    #   Python Testing With Python
    #   Intorduction To Algorithms
    assert context['user'].display_name == 'Test User'
    assert len(context['books']) == 2
    
def test_search(client, captured_templates):
    rv = client.get('/books/search?q=test')

    assert len(captured_templates) != 0
    template, context = captured_templates[0]

    assert template.name == 'search.html'
    assert context['title'] == 'bookshelf | Search'
    # Searching for a title containnig 'test' should result in results
    assert len(context['books']) > 0

@pytest.mark.parametrize('book_id, title, reading, reviewed', 
    [
        ('NLngYyWFl_YC', 'Introduction To Algorithms', True, False),
        ('hs_pAQAACAAJ', 'Python Testing with Pytest', False, True),
        ('CGVDDwAAQBAJ', 'Where the Crawdads Sing', False, False)

    ])
def test_book_details(client, mock_logged_in_user, captured_templates, \
    book_id, title, reading, reviewed):
    # Test cases:
    # 1. Book is not in firestore. No user reviews or active status
    # 2. Book is being read by user
    # 3. Book is reviewed by user
    session_cookie, uid = mock_logged_in_user.values()
    
    # Set mock request header for login required route
    client.set_cookie('localhost', 'firebase', session_cookie)
    
    # Add user to mock flask session
    with client.session_transaction() as sess:
        sess['_user'] = {
            'display_name': 'Test User',
            'uid': uid
        }
        sess.modified = True
    
    rv = client.get(f'/books/{book_id}')
    
    assert len(captured_templates) != 0
    template, context = captured_templates[0]

    assert template.name == 'book_details.html'
    assert context['title'] == f'bookshelf | {title}'
    # The database is pre-populated with one user: Test User
    # who has 2 books:
    #   Python Testing With Python
    #   Intorduction To Algorithms
    assert context['book'] != None
    # This will be used when updated
    """
    if reading or reviewed:
        assert context['book_user_info'] != None
    else:
        assert context['book_user_info'] == None
    
    if reviewed:
        assert context['book_reviews'] != None
    else:
        assert context['book_reviews'] == None
    """
    assert context['book_user_info'] != None
    assert context['book_reviews'] != None

def test_new_review_submit(client, mock_logged_in_user, mock_review_data):
    # Confirm form data is written to database:
    session_cookie, uid = mock_logged_in_user.values()
    
    # Set mock request header for login required route
    client.set_cookie('localhost', 'firebase', session_cookie)
    
    # Add user to mock flask session
    with client.session_transaction() as sess:
        sess['_user'] = {
            'display_name': 'Test User',
            'uid': uid
        }
        sess.modified = True

    book_id, form_data = mock_review_data

    # Mock request context wit form data
    rv = client.post(f'/books/review/new/{book_id}',  data=form_data)
    
    # Find book_review in db
    db = firestore.client()
    doc_ref = db.document(f'users/{uid}/books/{book_id}')
    doc = doc_ref.get()
    review = doc.to_dict()

    for k,v in form_data.items():
        if 'date' not in k:
            assert review[k] == v

def test_reading_request(client, mock_logged_in_user, mock_reading_data):

    # Confirm form data is written to database:
    session_cookie, uid = mock_logged_in_user.values()
    
    # Set mock request header for login required route
    client.set_cookie('localhost', 'firebase', session_cookie)
    
    # Add user to mock flask session
    with client.session_transaction() as sess:
        sess['_user'] = {
            'display_name': 'Test User',
            'uid': uid
        }
        sess.modified = True

    rv = client.post('/reading', json = mock_reading_data)

    # Check Request Data
    assert request.is_json
    assert request.get_json() == mock_reading_data

    # Check Response Data
    assert rv.status_code == 200
    assert rv.is_json

    # Check db update
    db = firestore.client()
    doc_ref = db.document(f"users/{uid}/books/{mock_reading_data['bookId']}")
    doc = doc_ref.get()
    book = doc.to_dict()
    print(book)
    assert book['date_started'] != None

