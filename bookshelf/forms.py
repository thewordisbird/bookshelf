from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, HiddenField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])

class ReviewForm(FlaskForm):
    rating = HiddenField('Rating', validators=[DataRequired()])
    review_title = StringField('Title')
    review_content = TextAreaField('Review')
    date_started = DateTimeField('Date Started', format='%m/%d/%Y')
    date_finished =DateTimeField('Date Finished', format='%m/%d/%Y')