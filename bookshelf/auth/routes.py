import os
import datetime

from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template, jsonify, abort, make_response, current_app, Blueprint, session

from .forms import LoginForm, RegisterForm, ResetPasswordForm
from flask_wtf.csrf import CSRFProtect

from bookshelf.firebase_auth import login_required, restricted, create_session_cookie, create_new_user, send_password_reset_email, set_custom_user_claims, decode_claims
from bookshelf.firebase_firestore import add_user

# Try moving this into factory
csrf = CSRFProtect(current_app)

bp = Blueprint('auth', __name__, static_folder='static')

class User:
    def __init__(self, display_name, email):
        self.display_name = display_name
        self.email = email
        self.id = None

    def to_dict(self):
        return self.__dict__


@bp.route('/', methods=['GET'])
def index():
    return "<h4>Index</h4>"


@bp.route('/register', methods=['GET', 'POST'])
def register():
    # Requires connection to firestore
    form = RegisterForm()

    if form.validate_on_submit():
        auth_user = create_new_user(form.data['email'], form.data['password'], form.data['name'])
        add_user({'display_name': form.data['name'] , 'email':form.data['email'] }, auth_user.uid)
        return redirect(url_for('auth.login'))        
    return render_template('register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if request.method == 'POST':
        id_token = request.form.get('idToken')
        expires_in = datetime.timedelta(days=5)
        try:
            session_cookie =  create_session_cookie(id_token, expires_in)
        except Exception:
            # TODO: respond with error to display message to user
            # see create_session_cookie function for info on possible errors
            return abort(401, 'Failed to create a session cookie')
        else:
            # TODO: Confirm user is in firestore & add them if not

            # Create Flask User session to store uid for user information lookup
            session['_user_id'] = request.form.get('uid')
            # Create response to client
            resp = jsonify({'status': 'success'})
            expires = datetime.datetime.now() + expires_in
            # CHANGE TO SECURE FOR PRODUCTION!!
            resp.set_cookie('firebase', session_cookie, expires=expires, httponly=True, secure=False)
            return resp
    return render_template('login.html', form=form, title="Login")


@bp.route('/profile', methods=['GET'])
@login_required
def access_restricted_content():
    session_cookie = request.cookies.get('firebase')
    #decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=True)
    #uid = decoded_claims.get('user_id')
    #email = decoded_claims.get('email')
    return render_template('profile.html')


@bp.route('/resetPassword', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        send_password_reset_email(form.data['email'])
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form=form, title='Reset Password')


@bp.route('/sessionLogout', methods=['POST'])
@csrf.exempt
def session_logout():
    print('in session logout')
    resp = jsonify({'status': 'success'})
    resp.set_cookie('firebase', expires=0)
    print(session['_user_id'])
    if '_user_id' in session:
        session.pop('_user_id')
    print(session.get('_user_id', None))
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
#comment
def check_admin():
    print(decode_claims(session['_user_id']))
    return redirect(url_for('auth.access_restricted_content'))