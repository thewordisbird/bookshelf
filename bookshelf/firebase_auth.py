import os
import json
from functools import wraps
import requests
from requests import HTTPError

import firebase_admin
from firebase_admin import auth

from flask import request, redirect, url_for, session, abort


    # Initialize Firebase in the application factory:
    #   import firebase-admin
    #   firebase_admin.initialize_app()
    # Requires the firebase-admin package installed and set enviornmental variable
    # GOOGLE_APPLICATION_CREDENTIALS pointing to the JSON file with service account key
    

# Decorators for login required and restricted access
def login_required(f):
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


def restricted(**claims):
    def decorator(f):
        def wrapper(*args, **kwargs):
            user_claims = auth.get_user(session['_user_id']).custom_claims
            if user_claims:
                for claim, value in claims.items():
                    if claim not in user_claims or user_claims[claim] != value:
                        return abort(401, 'You are not authorized to view this page :(')
                return f(*args, **kwargs)
            return abort(401, 'You are not authorized to view this page :(')
        return wrapper
    return decorator


def create_session_cookie(id_token, expires_in):
    print('in session cookie')
    try:
        # Create the session cookie. This will also verify the ID token in the process.
        # The session cookie will have the same claims as the ID token.
        print(type(id_token))
        session_cookie = auth.create_session_cookie(id_token, expires_in=expires_in)
        return session_cookie
    except Exception as e:
        # Possible Exceptions:
        #   - ValueError - If input parameters are invlaid
        #   - FirebseError - If an error occurs while creating a session cookie
        print(e)
        raise e


def create_new_user(email, password, display_name):
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

def add_auth_user(user):
    try:
        auth_user = auth.create_user(**user)
        return auth_user
    except Exception as e:
         # Possible Exceptions:
        #   - ValueError - If input parameters are invlaid
        #   - FirebseError - If an error occurs while creating a session cookie
        return e

def decode_claims(uid):
    return auth.get_user(uid).custom_claims

def set_custom_user_claims(uid, claims):
    try:
        auth.set_custom_user_claims(uid, claims)
    except Exception as e:
        # Possible Exceptions:
        #   - ValueError - If input parameters are invlaid
        #   - FirebseError - If an error occurs while creating a session cookie
        raise e

# REST API FOR TEMPLATE EMAIL ACTIONS
def raise_detailed_error(request_object):
    try:
        request_object.raise_for_status()
    except HTTPError as e:
        # raise detailed error message
        # TODO: Check if we get a { "error" : "Permission denied." } and handle automatically
        raise HTTPError(e, request_object.text)


def send_email_varification(id_token):
    endpoint = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode?key={os.environ.get('WEB_API_KEY')}"
    headers = {"content-type": "application/json; charset=UTF-8"}
    data = json.dumps({"requestType": "VERIFY_EMAIL", "idToken": id_token})
    request_object = requests.post(endpoint, headers=headers, data=data)
    raise_detailed_error(request_object)
    return request_object.json()


def send_password_reset_email(email):
    endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={os.environ.get('WEB_API_KEY')}"
    headers = {"content-type": "application/json; charset=UTF-8"}
    data = json.dumps({"requestType": "PASSWORD_RESET", "email": email})
    request_object = requests.post(endpoint, headers=headers, data=data)
    raise_detailed_error(request_object)
    return request_object.json()