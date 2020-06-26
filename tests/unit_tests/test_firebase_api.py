import pytest
import os
import json

from dotenv import load_dotenv, find_dotenv

import firebase_admin
from firebase_admin import credentials

from bookshelf.firebase_api import initialize_app

load_dotenv(find_dotenv())

GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_TEST_CREDENTIALS')

@pytest.fixture()
def firebase():
    yield initialize_app(GOOGLE_APPLICATION_CREDENTIALS)

@pytest.fixture()
def firestore(firebase):    
    yield firebase.firestore()

@pytest.fixture()
def populate_db(firestore):
    dirname = os.path.dirname(__file__)
    sample_collection_path = os.path.join(dirname, 'sample_collection.json')
    with open(sample_collection_path) as f:
        items = json.load(f)

        for item in items:
            firestore.set_document(f"users/{item['_id']}", item)
        
        yield items

        for item in items:
            firestore.delete_document(f"users/{item['_id']}")

@pytest.fixture()
def sample_document():
    dirname = os.path.dirname(__file__)
    sample_doc_path = os.path.join(dirname, 'sample_document.json')
    with open(sample_doc_path) as f:
        data = json.load(f)
        yield data

def test_envars():
    assert GOOGLE_APPLICATION_CREDENTIALS != None

def test_get_document(firestore, populate_db):
    items = populate_db
    for item in items:
        doc = firestore.get_document(f"users/{item['_id']}")
        assert doc['name'] == item['name']

def test_set_doc(firestore, sample_document):
    assert firestore.set_document(f"users/{sample_document['_id']}", sample_document) != None
    