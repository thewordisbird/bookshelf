import pytest

from bookshelf import create_app


@pytest.fixture
def app():
    app = create_app("testing")

    return app

@pytest.fixture(scope="function")
def auth(app):
    """Delete all authentecated users and yield auth object"""
    with app.app_context():
        auth = app.firebase.auth()
        #auth.clear_auth()
    
    yield auth

    #auth.clear_auth()


@pytest.fixture(scope="function")
def firestore(app):
    """Delete all data from firestore and yield firestore object"""
    with app.app_context():
        firestore = app.firebase.firestore()
        #firestore.clear_firestore()

    yield firestore

    #firestore.clear_firestore()
