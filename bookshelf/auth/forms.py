from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, HiddenField
from wtforms.validators import DataRequired, EqualTo

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    next = HiddenField('next', id='txtNext')

class RegisterForm(FlaskForm):
    display_name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match.')])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])

class ResetPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])