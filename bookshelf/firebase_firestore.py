from datetime import datetime
from firebase_admin import firestore

class User:
    def __init__(self, data):
        valid_attrs = {'display_name', 'email'}
        for key in data:
            if key in valid_attrs:
                setattr(self, key, data[key])
        self.timestamp = datetime.now()

    def to_dict(self):
        return self.__dict__


class Review:
    def __init__(self, data):
        valid_attrs = {book_id, display_name, uid, rating, date_started, date_finished, date_rated, review_title, review_content}
        for key in data:
            if key in valid_attrs:
                setattr(self, key, data[key])
        self.timestamp = datetime.now()

    def to_dict(self):
        return self.__dict__



def document_to_dict(doc):
    """Convert a Firestore document to dictionary"""
    if not doc.exists:
        return None
    doc_dict = doc.to_dict()
    doc_dict['id'] = doc.id
    return doc_dict
##
def add_user(user, user_id=None):
    # Take User object
    db = firestore.client()
    if user_id:
        use['last_update'] = datetime.now()
    else:
        user['created'] = datetime.now()
    user_ref = db.collection('users').document(user_id)
    user_ref.set(user)

def get_user(user_id):
    db = firestore.client()
    user_ref = db.collection('users').document(user_id)
    doc = user_ref.get()
    user = document_to_dict(doc)
    return user

def set_reading(user_id, book_id, start_date=None):
    db = firestore.client()
    book_ref = db.collection('users').document(user_id).collection('reading').document(book_id)
    if start_date == None:
        start_date = datetime.now()
    book_ref.set({'start_date': start_date})
    return document_to_dict(book_ref.get())

def get_reading_doc(user_id, book_id):
    db = firestore.client()
    book_ref =  book_ref = db.collection('users').document(user_id).collection('reading').document(book_id)
    book = book_ref.get()
    if book.exists:
        return document_to_dict(book)
    return None


def set_read(user_id, book_id, data):
    db = firestore.client()
    book_ref = db.collection('users').document(user_id).collection('read').document(book_id)
    # Add Timestamp to entry
    data['date_rated'] = datetime.now()
    book_ref.set(data)

update_read = set_read

def remove_reading_doc(user_id, book_id):
    db = firestore.client()
    book_ref = db.collection('users').document(user_id).collection('reading').document(book_id)
    book_ref.delete()

def get_read_doc(user_id, book_id):
    db = firestore.client()
    book_ref = db.collection('users').document(user_id).collection('read').document(book_id)
    book = book_ref.get()
    if book.exists:
        return document_to_dict(book)
    return None

def get_reviews(book_id):
    db = firestore.client()
    reviews = db.collection_group('read')
    docs = reviews.stream()
    for doc in docs:
        print(f'{doc.id} => {document_to_dict(doc)}')