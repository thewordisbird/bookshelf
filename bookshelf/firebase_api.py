import firebase_admin
from firebase_admin import auth, firestore, credentials

def initialize_app(key_path=None):
    """
    Returns an initialized Firebase object.

    For local development, requires a service account key. To download,
    goto console.firebase.google.com > Select Project > Project Settings >
    Service Accounts > Generate New Private Key. Save Key and set as 
    enviornmental variable
    """
    try:
        if key_path:
            cred = credentials.Certificate(key_path)            
        else:
            cred = credentials.ApplicationDefault()
    except ValueError:
        print('App already initialized')
    except Exception as e:
        print(f'error: {e}')
        raise e
    else:
        firebase_admin.initialize_app(cred)
    finally:
        return Firebase()


class Firebase:

    def auth(self):
        return Auth()

    def firestore(self):
        return Firestore()

class Auth:
    def welcome_user(self, name):
        print(f'hello, {name}')
    
    def create_session_cookie(self, id_token, expires_in):
    print('in session cookie')
    try:
        # Create the session cookie. This will also verify the ID token in the process.
        # The session cookie will have the same claims as the ID token.
        session_cookie = auth.create_session_cookie(id_token, expires_in=expires_in)
        return session_cookie
    except Exception as e:
        # Possible Exceptions:
        #   - ValueError - If input parameters are invlaid
        #   - FirebseError - If an error occurs while creating a session cookie
        print(e)
        raise e

    def create_new_user_with_email_password_display_name(self, email, password, display_name):
    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=display_name)
        return user
    except Exception as e:
        # Possible Exceptions:
        #   - ValueError - If input parameters are invlaid
        #   - FirebseError - If an error occurs while creating a session cookie
        return e


class Firestore:
    def set_document(self, document_path, data):
        db = firestore.client()
        doc_ref = db.document(document_path)
        return doc_ref.set(data)
    
    def get_document(self, document_path):
        db = firestore.client()
        doc_ref = db.document(document_path)
        doc = doc_ref.get()
        return doc.to_dict()

    def update_document(self, document_path, data):
        db = firestore.client()
        doc_ref = db.document(document_path)
        return doc_ref.update(data)

    def delete_document(self, document_path):
        db = firestore.client()
        doc_ref = db.document(document_path)
        return doc_ref.delete()
    

