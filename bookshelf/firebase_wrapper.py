import os
import json
import requests
import firebase_admin
from firebase_admin import auth, firestore, credentials
from functools import wraps
from flask import abort, request, redirect, url_for

class Firebase:

    def __init__(self, flask_app=None):
        self.flask_app = flask_app
        self.firebase_app = None

        if self.flask_app is not None:
            self.init_app(flask_app)

    def init_app(self, flask_app):
        """
        Returns an initialized Firebase object.

        For local development, requires a service account key. To download,
        goto console.firebase.google.com > Select Project > Project Settings >
        Service Accounts > Generate New Private Key. Save Key and set as 
        enviornmental variable
        """
        self.flask_app = flask_app
        cred_path = self.flask_app.config.get('GOOGLE_APPLICATION_CREDENTIALS')

        try:
            if cred_path:
                cred = credentials.Certificate(cred_path)            
            else:
                cred = credentials.ApplicationDefault()
        except ValueError:
            print('App already initialized')
        except Exception as e:
            print(f'error: {e}')
            raise e
        else:
            self.firebase_app = firebase_admin.initialize_app(cred)
                

    def delete_app(self):
        """Deletes the firebase connection"""
        # Probably needs error hadling incase already deleted. 
        firebase_admin.delete_app(self.firebase_app)

    def auth(self):
        return Auth()

    def firestore(self):
        return Firestore()
    
    def storage(self):
        pass


class Auth:

    @classmethod
    def login_required(cls, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print('in decorator')
            session_cookie = request.cookies.get('firebase')
            if not session_cookie:
                # Session cookie is unavailable. Force user to login.
                return redirect(url_for('auth.login', next=request.url))
            try:
                # Verify the session cookie. In this case an additional check is added to detect
                # if the user's Firebase session was revoked, user deleted/disabled, etc.
                auth.verify_session_cookie(session_cookie, check_revoked=True)
                return f(*args, **kwargs)
            except auth.InvalidSessionCookieError:
                # Session cookie is invalid, expired or revoked. Force user to login.
                return redirect(url_for('auth.login', next=request.url))
            # TODO: catch other possible exceptions:
            #   - ExpiredSessionCookieError – If the specified session cookie has expired.
            #   - RevokedSessionCookieError – If check_revoked is True and the cookie has been revoked.
            #   - CertificateFetchError – If an error occurs while fetching the public key certificates required to verify the session cookie.
        return decorated_function

    @classmethod
    def restricted(**claims):
        def decorator(f):
            def wrapper(*args, **kwargs):
                user_claims = auth.get_user(session['_user']['uid']).custom_claims
                if user_claims:
                    for claim, value in claims.items():
                        if claim not in user_claims or user_claims[claim] != value:
                            return abort(401, 'You are not authorized to view this page :(')
                    return f(*args, **kwargs)
                return abort(401, 'You are not authorized to view this page :(')
            return wrapper
        return decorator


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
        except Exception as e:
            # Possible Exceptions:
            #   - ValueError - If input parameters are invlaid
            #   - FirebseError - If an error occurs while creating a session cookie
            raise e
        else:
            return user

    def get_user(self, uid):
        return auth.get_user(uid)

    def update_user(self, uid, update_data):
        try:
            user = auth.update_user(uid, **update_data)
        except Exception as e:
            # Possible Exceptions:
            #   - ValueError - If input parameters are invlaid
            #   - FirebseError - If an error occurs while creating a session cookie
            raise e
        else:
            return user

    
    # REST API FOR TEMPLATE EMAIL ACTIONS
    def raise_detailed_error(self, request_object):
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
        self.raise_detailed_error(request_object)
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
        return list(map(self.doc_to_dict, docs))

    def get_collection_group(self, collection, filters=[], order_by=(), limit=25):
        # will need to create index in firebase console
        # kwargs for order_by, limit, etc
        db = firestore.client()
        docs_ref = db.collection_group(collection)
        
        # Build Query
        if order_by:
            docs_ref.order_by(order_by[0], direction=order_by[1])
        
        for filter in filters:
            docs_ref = docs_ref.where(filter[0], filter[1], filter[2])

        docs_ref.limit(limit)
        docs = docs_ref.stream()
        return list(map(self.doc_to_dict, docs))


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

    def doc_to_dict(self, doc):
        """Convert a Firestore document to dictionary"""
        if doc.exists:
            return doc.to_dict()           
        return None

    
                
