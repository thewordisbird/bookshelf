import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, HiddenField, DateField, FileField
from wtforms.validators import DataRequired, ValidationError, optional  

class NullableDateTimeField(DateTimeField):
    """Modify DateField to allow for Null values"""
    def process_formdata(self, valuelist):
        if valuelist:
            date_str = ' '.join(valuelist).strip()
            if date_str == '':
                self.data = None
                return
            try:
                self.data = datetime.datetime.strptime(date_str, self.format)
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid date value'))

class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])

class ReviewForm(FlaskForm):
    rating = HiddenField('Rating', validators=[DataRequired()])
    review_title = StringField('Headline')
    review_content = TextAreaField('Review')
    date_started = NullableDateTimeField('Date Started', format='%m/%d/%Y')
    date_finished = NullableDateTimeField('Date Finished', format='%m/%d/%Y')

    def validate_date_finished(self, date_finished):
        if self.date_started.data and date_finished.data:
            if self.date_started.data > date_finished.data:
                print("Date started must be lessthan or equal to date finished")
                raise ValidationError("Date started must be lessthan or equal to date finished.")
        
        elif self.date_started.data or date_finished.data:
            print('missing date')
            raise ValidationError("If setting read dates, both dates are required.")

class EditProfileForm(FlaskForm):
    valid_db_attrs = {
        'uid',
        'display_name',
        'email', 
        'created', 
        'last_updated'
    }
    valid_auth_attrs = {
        'uid',
        'display_name',
        'email',
        'email_verified',
        'phone_number',
        'photo_url',
        'password',
        'diabled',
        'app'
    }

    display_name = StringField('Display Name')
    phone_number = StringField('Phone Number')
    photo_url = FileField('Profile Photo')