import os
import datetime

from flask import Flask, flash, request, redirect, url_for, \
    render_template, jsonify, abort, current_app, Blueprint, session

from .forms import LoginForm, RegisterForm, ResetPasswordForm
from flask_wtf.csrf import CSRFProtect

import bookshelf.db_maint as db_maint

from bookshelf import firebase
auth = firebase.auth()
firestore = firebase.firestore()

# Add CSRF protection to post requests
csrf = CSRFProtect(current_app)

bp = Blueprint('auth', __name__, static_folder='static')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Form to register user with application.
    
    Create an auth user in firebase auth and duplicates the neccessary
    informaion into a user document in firestore.
    """
    form = RegisterForm()
    if form.validate_on_submit():
        email, password, display_name = form.data['email'], form.data['password'], form.data['display_name']        
        try:
            # Create new firebase auth user
            auth_user = auth.create_new_user_with_email_password_display_name(email, password, display_name)  
        except ValueError as v:
            # Covers Passwords being too short
            flash(v)
        except Exception as e:
            # TODO: Clean up depending on where in process error occured
            print(f'Auth Registration Error: {e.default_message}')
            flash(e.default_message)
        else:
            try:
                # Add successfully authorized user to firestore db
                db_user_data = {
                    'created': datetime.datetime.now(),
                    'display_name': display_name,
                    'email': email,
                    'last_updated': datetime.datetime.now()
                }
                # Add user to firestore
                firestore.set_document(f"users/{auth_user.uid}", db_user_data)            
            except Exception as e:
                # TODO: Clean up depending on where in process error occured
                print(f'User Database Error: {e}')
                flash('A problem arouse while trying to register. Please try again.')
            else:
                return redirect(url_for('auth.login')) 
    return render_template('register.html', title="bookshelf | Register", form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    ### CHANGE secure to True for production ###
    """
    Create session cookie from idToken passed from client

    On valid creation of session cookie, check to see if the user exists
    in the db, add if needed. 

    Stores User object in Flask session for quick access.
    """
    form = LoginForm(next = request.args.get('next') or '/')
    # Clear session:
    if '_user' in session:
        session.pop('_user')
    if request.method == 'POST':
        request_data = request.get_json()
        id_token, uid = request_data.values()
        expires_in = datetime.timedelta(days=5)
        try:
            session_cookie = auth.create_session_cookie(id_token, expires_in)    
        except Exception as e:
            # TODO: respond with error to display message to user
            # see create_session_cookie function for info on possible errors
            print(f'Login Error: {e}')
            return abort(401, 'Failed to create a session cookie')
        else:
            # Update db information for provider auth users
            auth_user = auth.get_user(request_data['uid'])._data
            
            providers = auth_user['providerUserInfo']
            google_provider = False
            for provider in providers:
                if provider['providerId'] == 'google.com':
                    google_provider = True  
            
            db_user = firestore.get_document(f"users/{uid}")
            if google_provider and db_user:
                # Upade db with provider info
                auth_user_data = {
                    'display_name': auth_user['displayName'],
                    'email': auth_user['email'],
                    'photo_url': auth_user["photoUrl"],
                }
                update_data = {}
                for k,v in auth_user_data.items():
                    if db_user.get(k, None) != v:
                        update_data[k] = auth_user_data[k]
                if update_data:
                    firestore.update_document(f"users/{uid}", update_data)
                    db_maint.update_user_data_in_books(uid, update_data)
            elif google_provider and not db_user:
                auth_user_data = {
                    'created': datetime.datetime.now(),
                    'display_name': auth_user['displayName'],
                    'email': auth_user['email'],
                    'photo_url': auth_user["photoUrl"],
                    'last_updated': datetime.datetime.now()
                }
                firestore.set_document(f"users/{uid}", auth_user_data)
            
            # Add user info to flask session
            session['_user'] = firestore.get_document(f"users/{uid}")
            session['_user']['uid'] = uid

            # Build Response
            resp = jsonify({'status': 'success'})
            expires = datetime.datetime.now() + expires_in
            # CHANGE TO SECURE FOR PRODUCTION!!
            resp.set_cookie('firebase', session_cookie, expires=expires, httponly=True, secure=True)
            return resp
    return render_template('login.html', title="bookshelf | Login", form=form, next=next)


@bp.route('/resetPassword', methods=['GET', 'POST'])
def reset_password():
    """Sends password reset to user"""
    form = ResetPasswordForm()
    if form.validate_on_submit():
        auth.send_password_reset_email(form.data['email'])
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', title="bookshelf | Reset Password", form=form)


@bp.route('/sessionLogout', methods=['POST'])
@csrf.exempt
def session_logout():
    """
    Log user out of application by removing flask session data and 
    firebase session cookie
    """
    resp = jsonify({'status': 'success'})
    resp.set_cookie('firebase', expires=0)
    if '_user' in session:
        session.pop('_user')
    return resp
