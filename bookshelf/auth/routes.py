import os
import datetime

from flask import Flask, flash, request, redirect, url_for, \
    render_template, jsonify, abort, current_app, Blueprint, session

from .forms import LoginForm, RegisterForm, ResetPasswordForm
from flask_wtf.csrf import CSRFProtect

from bookshelf import firebase

auth = firebase.auth()
firestore = firebase.firestore()

# Add CSRF protection to post requests
csrf = CSRFProtect(current_app)

bp = Blueprint('auth', __name__, static_folder='static')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Form to register collect user information to register user with app"""
    form = RegisterForm()
    if form.validate_on_submit():
        email, password, display_name = form.data['email'], form.data['password'], form.data['display_name']
        try:
            # Create new firebase auth user
            auth_user = auth.create_new_user_with_email_password_display_name(email, password, display_name)
            db_user_data = {
                'created': datetime.now(),
                'display_name': auth_user.display_name,
                'email': auth_user.email,
                'last_updated': datetime.datetime.now()
            }
            # Add user to firestore
            firestore.set_document(f"users/{auth_user.uid}", db_user_data)
            return redirect(url_for('auth.login'))      
        except Exception as e:
            # TODO: Clean up depending on where in process error occured
            print(f'Registration Error: {e}')
            flash('A problem arouse while trying to register. Please try again.')
            return redirect(url_for('auth.register'))
            #return abort(401, 'Unable to register')
    else:
        # TODO: User Friendly flashed errors
        for error in form.errors:
            flash(error)
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
        id_token, uid = request_data.values()
        expires_in = datetime.timedelta(days=5)
        try:
            session_cookie = auth.create_session_cookie(id_token, expires_in)    
        except Exception:
            # TODO: respond with error to display message to user
            # see create_session_cookie function for info on possible errors
            return abort(401, 'Failed to create a session cookie')
        else:
            user = firestore.get_document(f"users/{uid}")
            if user is None:
                auth_user = auth.get_user(request_data['uid'])
                db_user_data = {
                    'created': datetime.now(),
                    'display_name': auth_user.display_name,
                    'email': auth_user.email,
                    'last_updated': datetime.now()
                }
                user = firestore.set_document(f"users/{uid}", db_user_data)
            
            # Add user info to flask session
            session['_user'] = user

            resp = jsonify({'status': 'success'})
            expires = datetime.datetime.now() + expires_in
            # CHANGE TO SECURE FOR PRODUCTION!!
            resp.set_cookie('firebase', session_cookie, expires=expires, httponly=True, secure=False)
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
