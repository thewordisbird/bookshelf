from datetime import datetime
import firebase_admin
from firebase_admin import auth, firestore

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

    def __init__(self, data):
        for key in data:
            if key in self.valid_db_attrs or \
                key in self.valid_auth_attrs:
                setattr(self, key, data[key])
        #self.timestamp = datetime.now()

    def to_dict_for_auth(self):
        auth_dict = {key:self.__dict__[key] for key in self.valid_auth_attrs if key in self.__dict__}
        return auth_dict

    def to_dict_for_db(self):
        db_dict = {key:self.__dict__[key] for key in self.valid_db_attrs if key in self.__dict__}
        del db_dict['uid']
        return db_dict

    def to_dict(self):
        return self.__dict__

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

    def update_auth_data(self, auth_user):
        auth_user = auth_user.__dict__['_data']
        print(f'auth_user: {auth_user}')
        for key in auth_user.keys():
            if key in self.auth_field_map:
                setattr(self, self.auth_field_map[key], auth_user[key])
        # Update created from ms string to datetime
        self.created = datetime.fromtimestamp(int(self.created)/1000.0)
       
       