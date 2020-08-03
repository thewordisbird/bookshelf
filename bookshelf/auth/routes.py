import datetime
from flask import (
    flash,
    request,
    redirect,
    url_for,
    render_template,
    jsonify,
    abort,
    current_app,
    Blueprint,
    session,
)
from bookshelf import firebase
from .forms import LoginForm, RegisterForm, ResetPasswordForm
from flask_wtf.csrf import CSRFProtect
import bookshelf.db_maint as db_maint


auth = firebase.auth()
firestore = firebase.firestore()

# Add CSRF protection to post requests
csrf = CSRFProtect(current_app)

bp = Blueprint("auth", __name__, static_folder="static")


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Display register.html template for GET request and process register
    form data for POST request.

    For valid form submission, create an auth user in Firebase Auth
    and duplicates the neccessary informaion into a user document in firestore.

    """
    form = RegisterForm()

    if form.validate_on_submit():
        email, password, display_name = (
            form.data["email"],
            form.data["password"],
            form.data["display_name"],
        )
        try:
            # Create new firebase auth user
            auth_user = auth.create_new_user_with_email_password_display_name(
                email, password, display_name
            )
        except ValueError as v:
            # Display any errors to the user. The ValueError will handle
            # Password errors.
            flash(v)
        except Exception as e:
            # TODO: Add specific error handling.
            print(f"Auth Registration Error: {e.default_message}")
            flash(e.default_message)
        else:
            try:
                # If Firebase Auth successfully adds the user, add the user
                # information to Firestore.
                db_user_data = {
                    "created": datetime.datetime.now(),
                    "display_name": display_name,
                    "email": email,
                    "last_updated": datetime.datetime.now(),
                }

                firestore.set_document(f"users/{auth_user.uid}", db_user_data)
            except Exception as e:
                # TODO: Add specific error handling.
                print(f"User Database Error: {e}")
                flash("A problem arouse while trying to register. Please try again.")
            else:
                return redirect(url_for("auth.login"))

    return render_template("register.html", title="bookshelf | Register", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Display login.html template for GET request and set session cookie
    for POST request.

    The actuall login is processed on the front end with the JS SDK. A JWT
    is created and the idToken is passed to the backend to be converted to
    a session cookie. The session cookie is stored as the 'firebase' cookie.

    For users who login with google login, if this is the first time they
    attemp to login the user information will be copied to Firestore. For
    subsequent logins the user information is compared to the data stored
    in Firestore and updated if necessary.

    Stores User object in Flask session for quick access.

    """
    form = LoginForm(next=request.args.get("next") or "/")

    # Clear session:
    if "_user" in session:
        session.pop("_user")
    if request.method == "POST":
        request_data = request.get_json()
        id_token, uid = request_data.values()
        expires_in = datetime.timedelta(days=5)
        try:
            session_cookie = auth.create_session_cookie(id_token, expires_in)
        except Exception as e:
            # TODO: respond with error to display message to user
            # see create_session_cookie function for info on possible errors
            print(f"Login Error: {e}")
            return abort(401, "Failed to create a session cookie")
        else:
            # Update Firestore information for provider auth users.
            auth_user = auth.get_user(request_data["uid"])._data
            providers = auth_user["providerUserInfo"]
            google_provider = False

            for provider in providers:
                if provider["providerId"] == "google.com":
                    google_provider = True

            db_user = firestore.get_document(f"users/{uid}")

            if google_provider and db_user:
                # Upade Firestore with provider info.
                auth_user_data = {
                    "display_name": auth_user["displayName"],
                    "email": auth_user["email"],
                    "photo_url": auth_user["photoUrl"],
                }
                update_data = {}

                for k, v in auth_user_data.items():
                    if db_user.get(k, None) != v:
                        update_data[k] = auth_user_data[k]

                if update_data:
                    firestore.update_document(f"users/{uid}", update_data)
                    db_maint.update_user_data_in_books(uid, update_data)
            elif google_provider and not db_user:
                auth_user_data = {
                    "created": datetime.datetime.now(),
                    "display_name": auth_user["displayName"],
                    "email": auth_user["email"],
                    "photo_url": auth_user["photoUrl"],
                    "last_updated": datetime.datetime.now(),
                }
                firestore.set_document(f"users/{uid}", auth_user_data)

            # Add user info to flask session.
            session["_user"] = firestore.get_document(f"users/{uid}")
            session["_user"]["uid"] = uid

            # Build Response.
            resp = jsonify({"status": "success"})
            expires = datetime.datetime.now() + expires_in
            resp.set_cookie(
                "firebase",
                session_cookie,
                expires=expires,
                httponly=True,
                secure=current_app.config.get("SECURE_FIREBASE", True),
            )

            return resp

    return render_template(
        "login.html", title="bookshelf | Login", form=form, next=next
    )


@bp.route("/resetPassword", methods=["GET", "POST"])
def reset_password():
    """Sends password reset email to user.

    Uses Firebase template. Edit template in Firebase Console.

    """
    form = ResetPasswordForm()

    if form.validate_on_submit():
        try:
            auth.send_password_reset_email(form.data["email"])
        except Exception as e:
            print(f"Error:\n\t{e}")
        else:
            print(f"Password recovery email sent to {form.data['email']}")
        finally:
            return redirect(url_for("auth.login"))

    return render_template(
        "reset_password.html", title="bookshelf | Reset Password", form=form
    )


@bp.route("/sessionLogout", methods=["POST"])
@csrf.exempt
def session_logout():
    """Clear session cookie and flask session to log user out of app."""
    resp = jsonify({"status": "success"})
    resp.set_cookie("firebase", expires=0)
    if "_user" in session:
        session.pop("_user")
    return resp
