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

# Add CSRF protection to post requests
csrf = CSRFProtect(current_app)

bp = Blueprint('auth', __name__, static_folder='static')

def sans_csrf(data):
    """Remove CSRF From form data, convert rating to number"""
    del data['csrf_token']
    return data

@bp.route('/', methods=['GET'])
def index():
    return "<h4>Index</h4>"


@bp.route('/register', methods=['GET', 'POST'])
def register():
    # Requires connection to firestore
    form = RegisterForm()

    if form.validate_on_submit():
        user = User(sans_csrf(form.data))
        #auth_user = create_new_user(form.data['email'], form.data['password'], form.data['name'])
        auth_user = add_auth_user(user.to_dict())
        print(auth_user)
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
def check_admin():
    print(decode_claims(session['_user_id']))
    return redirect(url_for('auth.access_restricted_content'))