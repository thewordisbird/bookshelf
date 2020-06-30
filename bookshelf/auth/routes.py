import os
import datetime

from flask import Flask, flash, request, redirect, url_for, \
    send_from_directory, render_template, jsonify, abort, \
        make_response, current_app, Blueprint, session

from .forms import LoginForm, RegisterForm, ResetPasswordForm
from flask_wtf.csrf import CSRFProtect

from bookshelf.firebase_auth import login_required, restricted, \
    create_session_cookie, send_password_reset_email
from bookshelf.firebase_firestore import User, Review, add_user, get_user

from bookshelf.firebase_objects import User

# Add CSRF protection to post requests
csrf = CSRFProtect(current_app)

bp = Blueprint('auth', __name__, static_folder='static')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Form to register collect user information to register user with app"""
    form = RegisterForm()

    print(form.data, form.validate(), form.errors)
    if form.validate_on_submit():
        user = User(form.data)
        # -- UPDATE --
        # email, password, display_name = form.data['email'], form.data['password'], form.data['display_name']
        # -- END UPDATE --
        try:
            # -- UPDATE --
            # Create new firebase auth user
            # auth_user = auth.create_new_user_with_email_password_and_display_name()

            # Add user to firestore
            # firestore.set_document(f"users/{auth_user['uid']}", auth_user)
            # -- END UPDATE --

            auth_user = user.add_to_auth()
            user.update_auth_data(auth_user)
            user.add_to_db()
            
            return redirect(url_for('auth.login'))      
        except Exception as e:
            #TODO: Handle errors gracefully
            print(f'Registration Error: {e}')
            return abort(401, 'Unable to register')
    return render_template('register.html', title="bookshelf | Register", form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    ### CHANGE secure to True for production ###
    """Create session cookie from idToken passed from client

    On valid creation of session cookie, check to see if the user exists
    in the db, add if needed. 

    Stores User object in Flask session for quick access"""
    form = LoginForm(next = request.args.get('next') or '/')
    if request.method == 'POST':
        request_data = request.get_json()
        id_token = request_data['idToken']
        expires_in = datetime.timedelta(days=5)
        try:
            # -- UPDATE --
            # session_cookie = auth.create_session_cookie(id_token, expires_in)
            # -- END UPDATE --

            session_cookie =  create_session_cookie(id_token, expires_in)            
        except Exception:
            # TODO: respond with error to display message to user
            # see create_session_cookie function for info on possible errors
            return abort(401, 'Failed to create a session cookie')
        else:
            # -- UPDATE --
            # user = firestore.get_document(f"users/{request_data['uid']})
            # if user is None:
            #   auth_user = auth.get_user(request_data['uid'])
            #   user = firestore.set_document(f"users/{auth_user['uid']}", auth_user)
            #
            # session['_user'] = user
            # -- END UPDATE

            auth_user = User.build_from_auth(request_data['uid'])
            # Check if user is in firestore - users logged in with a provider
            # will need to be added to firestore on first login
            if not auth_user.exists_in_db():
                auth_user.add_to_db()

            user = User.build_from_db(auth_user.uid)
            print(f'login user: {user.to_dict()}')
            # Create Flask User session to store uid for user information lookup
            session['_user'] = user.to_dict()
            print(session['_user'])
            # Create response to client
            #next = request.args.get('next') or url_for('auth.index')
            #print(f'Next: {next}')

            resp = jsonify({'status': 'success'})
            expires = datetime.datetime.now() + expires_in
            # CHANGE TO SECURE FOR PRODUCTION!!
            resp.set_cookie('firebase', session_cookie, expires=expires, httponly=True, secure=False)
            print('RESP', resp)
            return resp
    return render_template('login.html', title="bookshelf | Login", form=form, next=next)


@bp.route('/resetPassword', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        # -- UPDATE --
        # auth.send_password_reset_email(form.data['email'])
        # -- END UPDATE

        send_password_reset_email(form.data['email'])
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', title="bookshelf | Reset Password", form=form)

@bp.route('/sessionLogout', methods=['POST'])
@csrf.exempt
def session_logout():
    print('in session logout')
    resp = jsonify({'status': 'success'})
    resp.set_cookie('firebase', expires=0)
    print('Session...:', session['_user'])
    if '_user' in session:
        session.pop('_user')
    print(session.get('_user', None))
    return resp
