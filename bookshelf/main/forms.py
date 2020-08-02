import datetime
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    DateTimeField,
    HiddenField,
    PasswordField,
)
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo


class NullableDateTimeField(DateTimeField):
    """Modify DateField to allow for Null values"""

    def process_formdata(self, valuelist):
        # Bypasses wtForms validation for blank datetime field.
        if valuelist:
            date_str = " ".join(valuelist).strip()
            if date_str == "":
                self.data = None
                return
            try:
                self.data = datetime.datetime.strptime(date_str, self.format)
            except ValueError:
                self.data = None
                raise ValueError(self.gettext("Not a valid date value"))


class SearchForm(FlaskForm):
    search = StringField("Search", validators=[DataRequired()])


class ReviewForm(FlaskForm):
    rating = HiddenField("Rating", validators=[DataRequired()])
    review_title = StringField("Headline")
    review_content = TextAreaField("Review")
    date_started = NullableDateTimeField("Date Started", format="%m/%d/%Y")
    date_finished = NullableDateTimeField("Date Finished", format="%m/%d/%Y")

    def validate_date_finished(self, date_finished):
        if self.date_started.data and date_finished.data:
            if self.date_started.data > date_finished.data:
                print("Date finished must be greater than or equal to date started")
                raise ValidationError(
                    "Date finished must be greater than or equal to date started."
                )

        elif self.date_started.data or date_finished.data:
            print("missing date")
            raise ValidationError("If setting read dates, both dates are required.")


class EditProfileForm(FlaskForm):
    display_name = StringField("Name", validators=[])
    email = StringField("Email", validators=[Email(message="Invalid Email Address.")])
    password = PasswordField(
        "Password",
        validators=[EqualTo("confirm_password", message="Passwords must match.")],
    )
    confirm_password = PasswordField("Confirm Password", validators=[])
