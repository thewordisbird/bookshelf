from datetime import datetime
import firebase_admin
from firebase_admin import auth, firestore

# User document
class User:
    """User object to control uniformity of input into firebase firestore
    and firebase auth.
    
    Modify valid_attrs to set valid fields for User Object
    """
    valid_db_attrs = {
        'uid',
        'display_name',
        'email', 
        'created', 
        'last_updated'
    }
    valid_auth_attrs = {
        'uid',
        'display_name',
        'email',
        'email_verified',
        'phone_number',
        'photo_url',
        'password',
        'diabled',
        'app'
    }

    # camelCase to snake_case key map for values returned from 
    # auth.get_user
    auth_field_map ={
        'localId': 'uid',
        'email': 'email',
        'displayName': 'display_name',
        'emailVerified': 'email_verified',
        'disabled': 'disabled',
        'createdAt': 'created'
    }
    # Methods for construction
    def __init__(self, data):
        for key in data:
            if key in self.valid_db_attrs or \
                key in self.valid_auth_attrs:
                setattr(self, key, data[key])
    
    @classmethod
    def build_from_db(cls, uid):
        db = firestore.client()
        user_ref = db.collection('users').document(uid)
        user = user_ref.get().to_dict()
        user['uid'] = uid
        return User(user)

    @classmethod
    def build_from_auth(cls, uid):
        auth_user = auth.get_user(uid).__dict__['_data']
        return User({cls.auth_field_map[key]: value for key, value in auth_user.items() \
            if key in cls.auth_field_map})

    # Methods for data manipulation
    def to_dict_for_auth(self):
        auth_dict = {key:self.__dict__[key] for key in self.valid_auth_attrs if key in self.__dict__}
        return auth_dict

    def to_dict_for_db(self):
        db_dict = {key:self.__dict__[key] for key in self.valid_db_attrs if key in self.__dict__}
        del db_dict['uid']
        return db_dict

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def document_to_dict(doc):
        """Convert a Firestore document to dictionary"""
        if not doc.exists:
            return None
        doc_dict = doc.to_dict()
        return doc_dict
    
    # Methods for auth CRUD
    def add_to_auth(self):
        """Adds a User object to firebase auth.
        
        Called in auth.register"""
        try:
            auth_user = auth.create_user(**self.to_dict_for_auth())
            return auth_user
        except Exception as e:
            # Possible Exceptions:
            #   - ValueError - If input parameters are invlaid
            #   - FirebseError - If an error occurs while creating a session cookie
            raise e
    
    # Methods for db CRUD
    def exists_in_db(self):
        db = firestore.client()
        user_ref =  db.collection('users').document(self.uid)
        user = user_ref.get()
        return user.exists

    def add_to_db(self):
        db = firestore.client()
        self.created = datetime.fromtimestamp(int(self.created)/1000.0)
        setattr(self, 'last_updated', self.created)
        user_ref = db.collection('users').document(self.uid)
        user_ref.set(self.to_dict_for_db())

    def update_db(self, update_data):
        db = firestore.client()
        user_ref = db.collection('users').document(self.uid)
        user_ref.update(update_data)
        for k,v in update_data.items():
            setattr(self, k, v)

    def update_auth_data(self, auth_user):
        auth_user = auth_user.__dict__['_data']
        print(f'auth_user: {auth_user}')
        for key in auth_user.keys():
            if key in self.auth_field_map:
                setattr(self, self.auth_field_map[key], auth_user[key])
        # Update created from ms string to datetime
        self.created = datetime.fromtimestamp(int(self.created)/1000.0)
    
    def get_books(self):
        db = firestore.client()
        books =  db.collection('users').document(self.uid).collection('books')
        docs = books.stream()
        return list(map(User.document_to_dict, docs))
       
# Book documents
class Book:
    valid_db_attrs = {
        'uid',
        'bid',
        'title',
        'authors',
        'cover_url',
        'rating',
        'review_title',
        'review_content',
        'date_started',
        'date_finished',
        'date_rated',
        'created',
        'last_updated',
        'display_name'
    }
    
    def __init__(self, data):
        self.last_updated = datetime.now()
        for key in data:
            if key in self.valid_db_attrs:
                setattr(self, key, data[key])

    @classmethod
    def build_from_db(cls, uid, bid):
        data = {
            'uid': uid,
            'bid': bid
        }
        db = firestore.client()
        book_ref = db.collection('users').document(uid).collection('books').document(bid)
        book = book_ref.get()
        
        print(f'Book get from fs:\n" {book.__dict__}, exists {book.exists}\n')
        if book.exists:
            data.update(book.__dict__['_data'])
            return Book(data)
        return Book(data)

    @staticmethod
    def document_to_dict(doc):
        """Convert a Firestore document to dictionary"""
        if not doc.exists:
            return None
        doc_dict = doc.to_dict()
        return doc_dict
    
    def write_to_db(self):
        db = firestore.client()
        book_ref = db.collection('users').document(self.uid).collection('books').document(self.bid)
        book_ref.set(self.__dict__)

    

    @classmethod
    def get_all_reviews(cls, bid):
        #print(bid)
        db = firestore.client()
        reviews = db.collection_group('books').where('bid', '==', bid)
        docs = reviews.stream()
        #for doc in docs:
        #    print(f'{doc.id} => {doc.to_dict()}')
        return list(map(Book.document_to_dict, docs))

    @classmethod
    def get_all_books(cls):
        db = firestore.client()
        books = db.collection_group('books').order_by('last_updated', 'DESCENDING')
        docs = books.stream()
        return list(map(Book.document_to_dict, docs))

    

if __name__ == '__main__':
    firebase_admin.initialize_app()
    bid = 'fn20CwAAQBAJ' 
    uid = 'qAO4fDECt3NgB1tjbFF4nlWjZUj2'

    #book = Book.build_from_db(uid, bid)
    #print(book.__dict__)

    #Book.get_all_reviews(bid)
    Book.get_all_user_by_book(bid)


    