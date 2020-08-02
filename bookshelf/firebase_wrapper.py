import json
import requests
import firebase_admin
from firebase_admin import auth, firestore, credentials
from functools import wraps
from flask import abort, request, redirect, url_for, session


class Firebase:
    """Wrapper for Google Firebase.

    Abstraction of Firebase Admin SDK and REST API for access to Firebase
    Auth and Firestore.

    TODO: Incorporate Storage API.

    """

    def __init__(self):
        """Instantiate Firebase Class."""
        self.google_application_credentials = None
        self.api_key = None

    def init_app(self, google_application_credentials, web_api_key):
        """Returns an initialized Firebase object.

        Requires a service account key. To download goto
        console.firebase.google.com > Select Project > Project Settings >
        Service Accounts > Generate New Private Key. Save Key and set as
        enviornmental variable.

        Args:
            google_application_credentials (str): Path to service account key.
            web_api_key (str): Google Web API Key.

        """
        self.google_application_credentials = google_application_credentials
        self.web_api_key = web_api_key

        if not firebase_admin._apps:
            try:
                if self.google_application_credentials:
                    cred = credentials.Certificate(self.google_application_credentials)
                else:
                    cred = credentials.ApplicationDefault()
            except ValueError:
                print("App already initialized")
            except Exception as e:
                print(f"error: {e}")
                raise e
            else:
                print("initializing app")
                self.firebase_app = firebase_admin.initialize_app(cred)

    def delete_app(self):
        """Deletes the firebase app connection"""
        firebase_admin.delete_app(self.firebase_app)

    def auth(self):
        """Return an Auth ojbect."""
        return Auth(self.web_api_key)

    def firestore(self):
        """Return a Firestore object."""
        return Firestore()

    def storage(self):
        """Return Firebase Storage object."""
        pass


class Auth:
    """Wrapper for Firebase Auth."""

    def __init__(self, web_api_key):
        """Instansiate Auth object.

        Not used publicly. Requires the Firebase app to be initiated first.

        Args:
            web_api_key (str): Google Web API Key.

        """
        self.web_api_key = web_api_key

    @classmethod
    def login_required(cls, f):
        # TODO: Should be moved into helper file to keep modular and light for
        #       usage not including flask.
        @wraps(f)
        def decorated_function(*args, **kwargs):
            session_cookie = request.cookies.get("firebase")
            if not session_cookie:
                # Session cookie is unavailable. Force user to login.
                return redirect(url_for("auth.login", next=request.url))
            try:
                # Verify the session cookie. In this case an additional check is added to detect
                # if the user's Firebase session was revoked, user deleted/disabled, etc.
                auth.verify_session_cookie(session_cookie, check_revoked=True)
                return f(*args, **kwargs)
            except auth.InvalidSessionCookieError:
                # Session cookie is invalid, expired or revoked. Force user to login.
                return redirect(url_for("auth.login", next=request.url))
            # TODO: catch other possible exceptions:
            #   - ExpiredSessionCookieError – If the specified session cookie has expired.
            #   - RevokedSessionCookieError – If check_revoked is True and
            #       the cookie has been revoked.
            #   - CertificateFetchError – If an error occurs while fetching the
            #       public key certificates required to verify the session cookie.

        return decorated_function

    @classmethod
    def restricted(**claims):
        # TODO:Should be moved into helper file to keep modular and light for
        #       usage not including flask.
        # Validates user claims to determine if the user is allowed access
        # to restricted content.
        def decorator(f):
            def wrapper(*args, **kwargs):
                user_claims = auth.get_user(session["_user"]["uid"]).custom_claims
                if user_claims:
                    for claim, value in claims.items():
                        if claim not in user_claims or user_claims[claim] != value:
                            return abort(
                                401, "You are not authorized to view this page :("
                            )
                    return f(*args, **kwargs)
                return abort(401, "You are not authorized to view this page :(")

            return wrapper

        return decorator

    def create_session_cookie(self, id_token, expires_in):
        """Create session cookie from firebase idToken.

        Args:
            id_token (str): Firebase idToken.
            expires_in (datetime.timedelta): Lifespan of session cookie.

        """
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

    def create_new_user_with_email_password_display_name(
        self, email, password, display_name
    ):
        """Create new user.

        Creates new Auth user with email, password and display name.

        Args:
            email (str): User email address.
            password (str): User password.
            display_name (str): User display name.

        Returns:
            UserRecord: A user record instance for the newly created user.

        """
        try:
            user = auth.create_user(
                email=email, password=password, display_name=display_name
            )
        except Exception as e:
            # Possible Exceptions:
            #   - ValueError - If input parameters are invlaid
            #   - FirebseError - If an error occurs while creating a session cookie
            raise e
        else:
            return user

    def get_user(self, uid):
        """Get authenticated user record.

        Args:
            uid (str): User ID.

        Returns:
            UserRecord: A user record instance for the uid.

        """
        return auth.get_user(uid)

    def update_user(self, uid, update_data):
        """Update user information.

        Args:
            update_data (dict): Data fields to update.

        Returns:
            UserRecord: A user record instance for the updated user.

        For a list of valid data fields see firebase auth documentation:
            https://firebase.google.com/docs/reference/admin/python/firebase_admin.auth#update_user

        """
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
        except Exception as e:
            # raise detailed error message
            # TODO: Check if we get a { "error" : "Permission denied." } and handle automatically
            raise Exception(e, request_object.text)

    def send_password_reset_email(self, email):
        """Send password reset email using firebase email template.

        Args:
            email (str): User email address

        Returns:
            JSON: Response object indicating the status of the request.

        """

        endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={self.web_api_key}"
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"requestType": "PASSWORD_RESET", "email": email})
        request_object = requests.post(endpoint, headers=headers, data=data)
        self.raise_detailed_error(request_object)
        return request_object.json()

    def clear_auth(self):
        pass


class Firestore:
    """Wrapper for Firebase Firestore."""

    def set_document(self, document_path, data):
        """Store document in Firestore.

        Args:
            document_path (str): Path to document.
            data (dict): Data to be stored.

        Returns:
            WritreResult: Tupple containing update_time and document reference.

        """
        db = firestore.client()
        doc_ref = db.document(document_path)
        return doc_ref.set(data)

    def get_document(self, document_path):
        """Retreive document from Firestore.

        Args:
            document_path (str): Path to document.

        Returns:
            dict: Python dictionary with document data.

        """
        db = firestore.client()
        doc_ref = db.document(document_path)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None

    def update_document(self, document_path, data):
        """Update Firestore document.

        Args:
            document_path (str): Path to document.
            data (dict): Data to be updated.

        Returns:
            WritreResult: Tupple containing update_time and document reference.

        """
        db = firestore.client()
        doc_ref = db.document(document_path)
        return doc_ref.update(data)

    def delete_document(self, document_path):
        """Delete document from Firestore.

        Args:
            document_path (str): Path to document.

        Returns:
            Timestamp: Timestamp object of deletion.

        """
        db = firestore.client()
        doc_ref = db.document(document_path)
        return doc_ref.delete()

    def get_collection(self, collection_path, limit=25):
        """Retreive all documents in collection.

        Args:
            collection_path (str): Path to collection.
            limit (int): Number of documents to retrieve per query. Default set to 25.

        Returns:
            list: Python list with dictionary for each document in collection.

        """
        db = firestore.client()
        docs_ref = db.collection(collection_path)
        docs = docs_ref.stream()
        return list(map(self.doc_to_dict, docs))

    def get_collection_group(self, collection, filters=[], order_by=(), limit=25):
        """Retreuve all documents in collection group.

        Requires index created in firebase console. On first run a link will be
        provided to create the index.

        Args:
            collection (str): Collection name. This method will query all data
                in any collection with this name.
            filters (list): List of filters to apply to the query.
            order_by (tuple): Tuple containing field and ASCENDING/DESCENDING.
            limit (int): Number of documents to retrieve per query. Default set to 25.

        Returns:
            list: Python list with dictionary for each document in collection.

        """
        db = firestore.client()
        docs_ref = db.collection_group(collection)

        # Build Query
        if order_by:
            docs_ref = docs_ref.order_by(order_by[0], direction=order_by[1])

        for filter in filters:
            docs_ref = docs_ref.where(filter[0], filter[1], filter[2])

        docs_ref.limit(limit)
        docs = docs_ref.stream()
        return list(map(self.doc_to_dict, docs))

    def set_documents_from_json(self, collection_path, json_file_path):
        """Add documents to Firestore from a JSON file.

        Args:
            collection_path (str): Path to collection.
            json_file_path (str): Path to JSON document.

        """
        db = firestore.client()
        with open(json_file_path) as f:
            data = json.load(f)

        for item in data:
            doc_ref = db.document(f"{collection_path}/{item['_id']}")
            doc_ref.set(item)

    def doc_to_dict(self, doc):
        """Convert a Firestore document to dictionary.

        Args:
            doc (Document): Firestore Document object.

        Returns:
            dict: Python dictionary with document data.

        """
        if doc.exists:
            d = doc.to_dict()
            d["doc_id"] = doc.id
            return d
        return None

    def clear_firestore(self):
        pass
