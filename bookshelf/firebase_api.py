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
    
    def storage(self):
        pass


class Auth:
    def welcome_user(self, name):
        print(f'hello, {name}')
    
    def create_session_cookie(self, id_token, expires_in):
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

    def get_user(self, uid):
        return auth.get_user(uid)

    
    # REST API FOR TEMPLATE EMAIL ACTIONS
    @staticmethod
    def raise_detailed_error(request_object):
        try:
            request_object.raise_for_status()
        except HTTPError as e:
            # raise detailed error message
            # TODO: Check if we get a { "error" : "Permission denied." } and handle automatically
            raise HTTPError(e, request_object.text)

    def send_password_reset_email(self, email):
        endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={os.environ.get('WEB_API_KEY')}"
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"requestType": "PASSWORD_RESET", "email": email})
        request_object = requests.post(endpoint, headers=headers, data=data)
        raise_detailed_error(request_object)
        return request_object.json()


class Firestore:
    def set_document(self, document_path, data):
        db = firestore.client()
        doc_ref = db.document(document_path)
        return doc_ref.set(data)
    
    def get_document(self, document_path):
        db = firestore.client()
        doc_ref = db.document(document_path)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None

    def get_collection(self, collection_path, limit=25):
        db = firestore.client()
        docs_ref =  db.collection(collection_path)
        docs = docs_ref.stream()
        return list(map(document_to_dict, docs))

    def get_collection_group(self, collection, **kwargs):
        # will need to create index in firebase console
        # kwargs for order_by, limit, etc
        db = firestore.client()
        docs_ref = db.collection_group(collection).order_by()
        docs = docs.stream()
        return list(map(document_to_dict, docs))


    def update_document(self, document_path, data):
        db = firestore.client()
        doc_ref = db.document(document_path)
        return doc_ref.update(data)

    def delete_document(self, document_path):
        db = firestore.client()
        doc_ref = db.document(document_path)
        return doc_ref.delete()
    
    def set_documents_from_json(self, collection_path, json_file_path):
        db = firestore.client()
        with open(json_file_path) as f:
            data = json.load(f)
            for item in data:
                doc_ref = db.document(f"{collection_path}/item['_id']")
                doc_ref.set(item)

    @staticmethod
    def document_to_dict(document)
        """Convert a Firestore document to dictionary"""
        if document.exists:
            doc_dict = doc.to_dict()
            return doc_dict            
        return None

    
                
