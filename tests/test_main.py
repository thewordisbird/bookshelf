import pytest
from flask import url_for
from firebase_admin import firestore

def test_index(client):
    assert client.get(url_for('books.index')).status_code == 200


def test_profile(client, app_user, captured_templates):
    assert app_user.session_cookie != None
    assert app_user.uid != None
    assert app_user.display_name == "Test User"

    # Set mock request header
    client.set_cookie('localhost', 'firebase', app_user.session_cookie)

     # Add user to mock flask session
    with client.session_transaction() as sess:
        sess['_user'] = {
            'display_name': app_user.display_name,
            'uid': app_user.uid
        }
        sess.modified = True
   
    rv = client.get(url_for('books.profile', user_id=app_user.uid))

    assert len(captured_templates) != 0
    template, context = captured_templates[0]

    assert template.name == 'profile.html'
    assert context['title'] == 'bookshelf | Test User'
    assert context['user']['display_name'] == app_user.display_name
    # TODO: Load books into db. Serialization issue. See conftest.py
    assert len(context['books_reading']) == 1
    assert len(context['books_read']) == 1

def test_edit_profile_get(client, app_user, captured_templates):
    assert app_user.session_cookie != None
    assert app_user.uid != None
    assert app_user.display_name == "Test User"

    # Set mock request header
    client.set_cookie('localhost', 'firebase', app_user.session_cookie)

     # Add user to mock flask session
    with client.session_transaction() as sess:
        sess['_user'] = {
            'display_name': app_user.display_name,
            'uid': app_user.uid
        }
        sess.modified = True

    rv = client.get(url_for('books.edit_profile', user_id=app_user.uid))
    
    assert len(captured_templates) != 0
    template, context = captured_templates[0]

    assert template.name == 'edit_profile_form.html'
    assert context['title'] == 'bookshelf | edit | Test User'
    

def test_edit_profile_post(client, app_user, captured_templates):
    assert app_user.session_cookie != None
    assert app_user.uid != None
    assert app_user.display_name == "Test User"

    # Set mock request header
    client.set_cookie('localhost', 'firebase', app_user.session_cookie)
    # Edit data
    edit_data = {
        "display_name": "User Test",
        "email": "test_user@email.com",
        "password": "",
        "confirm_password": ""
    }

    # Add user to mock flask session
    with client.session_transaction() as sess:
        sess['_user'] = {
            'display_name': app_user.display_name,
            'uid': app_user.uid
        }
        sess.modified = True

    rv = client.post(url_for('books.edit_profile', user_id=app_user.uid), \
        data=edit_data, follow_redirects=True)

    assert len(captured_templates) != 0
    template, context = captured_templates[0]

    assert template.name == 'profile.html'
    assert context['title'] == 'bookshelf | User Test'


def test_search(client, captured_templates):
    rv = client.get(url_for('books.search', q="python"))

    assert len(captured_templates) != 0
    template, context = captured_templates[0]

    assert template.name == 'search.html'
    assert context['title'] == 'bookshelf | Search'
    assert len(context['books']) == 25


def test_book_details_no_user(client, captured_templates):
    # Book id for "Where the Crawdads Sing"
    rv = client.get(url_for('books.book_details', book_id="CGVDDwAAQBAJ"))

    assert len(captured_templates) != 0
    template, context = captured_templates[0]

    assert template.name == 'book_details.html'
    assert context['title'] == 'bookshelf | Where the Crawdads Sing'
    assert context['book_user_info'] == None

def test_book_details_logged_in(client, app_user, captured_templates):
    # Set mock request header
    client.set_cookie('localhost', 'firebase', app_user.session_cookie)

    # Add user to mock flask session
    with client.session_transaction() as sess:
        sess['_user'] = {
            'display_name': app_user.display_name,
            'uid': app_user.uid
        }
        sess.modified = True

    # Book id for "Where the Crawdads Sing"
    rv = client.get(url_for('books.book_details', book_id="CGVDDwAAQBAJ"))

    assert len(captured_templates) != 0
    template, context = captured_templates[0]

    assert template.name == 'book_details.html'
    assert context['title'] == 'bookshelf | Where the Crawdads Sing'
    assert context['book_user_info'] != None
    # TODO: Add reviews to make sure they are passed through. 
    # For a logged in user they should show the users review first and 
    # All reviews below

def test_new_review_get(client, app_user, captured_templates):
    # Set mock request header
    client.set_cookie('localhost', 'firebase', app_user.session_cookie)

    # Add user to mock flask session
    with client.session_transaction() as sess:
        sess['_user'] = {
            'display_name': app_user.display_name,
            'uid': app_user.uid
        }
        sess.modified = True

    # Book id for "Where the Crawdads Sing"
    client.get(url_for('books.new_review', book_id='wcd8DgAAQBAJ'))

    #assert "1984" in rv.get_data(as_text=True)
    assert len(captured_templates) != 0
    template, context = captured_templates[0]

    assert template.name == 'review_form.html'
    assert context['book']['volumeInfo']['title'] == 'Unbroken'

def test_new_review_put(client, app_user, captured_templates):
    

    # Set mock request header
    client.set_cookie('localhost', 'firebase', app_user.session_cookie)

    # Add user to mock flask session
    with client.session_transaction() as sess:
        sess['_user'] = {
            'display_name': app_user.display_name,
            'uid': app_user.uid
        }
        sess.modified = True

    review_data = {
        "rating": 5,
        "review_title": "Test Review Title",
        "review_content": "Test Review Content",
        "date_started": "",
        "date_finished": "",
    }

    # Book id for "Where the Crawdads Sing"
    client.post(url_for('books.new_review', book_id='wcd8DgAAQBAJ'), \
        data=review_data, follow_redirects=True)

    # Check that review exists in firestore
    db = firestore.client()
    doc_ref = db.document(f"users/{app_user.uid}/books/wcd8DgAAQBAJ")
    doc = doc_ref.get()
    assert doc.exists
    book = doc.to_dict()
    assert book['rating'] == review_data['rating']

    assert len(captured_templates) != 0
    template, context = captured_templates[0]
    assert template.name == 'book_details.html'
    assert context['book']['volumeInfo']['title'] == 'Unbroken'

def test_edit_review(client, app_user, captured_templates):
    # Set mock request header
    client.set_cookie('localhost', 'firebase', app_user.session_cookie)

    # Add user to mock flask session
    with client.session_transaction() as sess:
        sess['_user'] = {
            'display_name': app_user.display_name,
            'uid': app_user.uid
        }
        sess.modified = True

    review_data = {
        "rating": 5,
        "review_title": "Test Review Title",
        "review_content": "Test Review Content",
        "date_started": "",
        "date_finished": "",
    }

    # Book id for "Where the Crawdads Sing"
    client.post(url_for('books.new_review', book_id='wcd8DgAAQBAJ'), \
        data=review_data, follow_redirects=True)

    # Check that review exists in firestore
    db = firestore.client()
    doc_ref = db.document(f"users/{app_user.uid}/books/wcd8DgAAQBAJ")
    doc = doc_ref.get()
    assert doc.exists
    book = doc.to_dict()
    assert book['rating'] == review_data['rating']

    edit_review_data = {
        "rating": 4,
        "review_title": "Test Review Title - Edit",
        "review_content": "Test Review Content",
        "date_started": "",
        "date_finished": "",
    }

    client.post(url_for('books.edit_review', book_id='wcd8DgAAQBAJ'), \
        data=edit_review_data, follow_redirects=True)

    # Check that review exists in firestore
    db = firestore.client()
    doc_ref = db.document(f"users/{app_user.uid}/books/wcd8DgAAQBAJ")
    doc = doc_ref.get()
    assert doc.exists
    book = doc.to_dict()
    assert book['rating'] == edit_review_data['rating']

    assert len(captured_templates) != 0
    template, context = captured_templates[0]
    assert template.name == 'book_details.html'
    assert context['book']['volumeInfo']['title'] == 'Unbroken'

def test_reading(client, app_user):
    

    # Set mock request header
    client.set_cookie('localhost', 'firebase', app_user.session_cookie)

    # Add user to mock flask session
    with client.session_transaction() as sess:
        sess['_user'] = {
            'display_name': app_user.display_name,
            'uid': app_user.uid
        }
        sess.modified = True

    # Book id for "Where the Crawdads Sing"
    json_data = {"bookId": "wcd8DgAAQBAJ" }
    client.post(url_for('books.reading'), json=json_data)

    # Check that review exists in firestore
    db = firestore.client()
    doc_ref = db.document(f"users/{app_user.uid}/books/wcd8DgAAQBAJ")
    doc = doc_ref.get()
    assert doc.exists
    book = doc.to_dict()
    assert book['date_started'] != None


