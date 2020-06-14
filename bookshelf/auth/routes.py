import os
import datetime

from flask import Flask, flash, request, redirect, url_for, \
    send_from_directory, render_template, jsonify, abort, \
        make_response, current_app, Blueprint, session

from .forms import LoginForm, RegisterForm, ResetPasswordForm
from flask_wtf.csrf import CSRFProtect

from bookshelf.firebase_auth import login_required, restricted, \
    create_session_cookie, create_new_user, send_password_reset_email, \
        set_custom_user_claims, decode_claims, add_auth_user
from bookshelf.firebase_firestore import User, Review, add_user, get_user

from bookshelf.firebase_objects import User

# Add CSRF protection to post requests
csrf = CSRFProtect(current_app)

bp = Blueprint('auth', __name__, static_folder='static')

def sans_csrf(data):
    """Remove CSRF From form data, convert rating to number"""
    del data['csrf_token']
    return data


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Form to register collect user information to register user with app"""
    form = RegisterForm()

    print(form.data, form.validate(), form.errors)
    if form.validate_on_submit():
        user = User(form.data)
        print(f'route user obj: {user.__dict__}')
        try:
            user.add_to_auth()
            return redirect(url_for('auth.login'))      
        except Exception as e:
            #TODO: Handle errors gracefully
            print(f'Registration Error: {e}')
            return abort(401, 'Unable to register')
    return render_template('register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    ### CHANGE secure to True for production ###
    """Create session cookie from idToken passed from client

    On valid creation of session cookie, check to see if the user exists
    in the db, add if needed. 

    Stores User object in Flask session for quick access"""
    form = LoginForm()
    next = request.args.get('next') or '/'
    if request.method == 'POST':
        
        #print(f"the next hop:{form.data['next']}")
        id_token = request.form.get('idToken')
        expires_in = datetime.timedelta(days=5)
        try:
            session_cookie =  create_session_cookie(id_token, expires_in)
        except Exception:
            # TODO: respond with error to display message to user
            # see create_session_cookie function for info on possible errors
            return abort(401, 'Failed to create a session cookie')
        else:
            auth_user = User.build_from_auth(request.form.get('uid'))
            # Check if user is in firestore - users logged in with a provider
            # will need to be added to firestore on first login
            if not auth_user.exists_in_db():
                auth_user.add_to_db()
            # Create Flask User session to store uid for user information lookup
            session['_user'] = auth_user.to_dict()
            print(session['_user'])
            # Create response to client
            #next = request.args.get('next') or url_for('auth.index')
            #print(f'Next: {next}')
            resp = jsonify({'status': 'success'})
            expires = datetime.datetime.now() + expires_in
            # CHANGE TO SECURE FOR PRODUCTION!!
            resp.set_cookie('firebase', session_cookie, expires=expires, httponly=True, secure=False)
            return resp
    return render_template('login.html', form=form, next=next, title="Login")





@bp.route('/resetPassword', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        send_password_reset_email(form.data['email'])
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form=form, title='Reset Password')

@bp.route('/logout')
def logout():
    return render_template('logout.html')

@bp.route('/sessionLogout', methods=['POST'])
@csrf.exempt
def session_logout():
    print('in session logout')
    resp = jsonify({'status': 'success'})
    resp.set_cookie('firebase', expires=0)
    print(session['_user'])
    if '_user' in session:
        session.pop('_user')
    print(session.get('_user', None))
    return resp


@bp.route('/adminOnly')
@restricted(admin=True)
def admin_only():
    return render_template('admin_only.html', title='Admin')


@bp.route('/makeAdmin')
def set_admin():
    print(decode_claims(session['_user_id']))
    set_custom_user_claims(session['_user_id'], {'admin': True})
    print(decode_claims(session['_user_id']))
    return redirect(url_for('auth.access_restricted_content'))

@bp.route('/checkAdmin')
def check_admin():
    print(decode_claims(session['_user_id']))
    return redirect(url_for('auth.access_restricted_content'))