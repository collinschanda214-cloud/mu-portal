from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, TextAreaField, SelectField,
                     SubmitField, IntegerField, DateField)
from wtforms.validators import (DataRequired, Length, EqualTo, Email,
                                Regexp, Optional, NumberRange)

class LoginForm(FlaskForm):
    student_number = StringField("Student Number", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class TicketForm(FlaskForm):
    subject = StringField("Subject", validators=[DataRequired()])
    category = SelectField("Category", choices=[
        ("Accounts","Accounts"),("Academics","Academics"),
        ("ICT","ICT"),("Accommodation","Accommodation"),("Other","Other")])
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Submit Ticket")

class PasswordForm(FlaskForm):
    current = PasswordField("Current Password", validators=[DataRequired()])
    new = PasswordField("New Password", validators=[
        DataRequired(),
        Length(min=5, max=5, message="Password must be exactly 5 characters"),
        Regexp(r"^[A-Za-z0-9]+$", message="Only letters and numbers allowed")])
    confirm = PasswordField("Confirm Password",
        validators=[DataRequired(), EqualTo("new", message="Passwords must match")])
    submit = SubmitField("Update Password")

class RegisterForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name  = StringField("Last Name",  validators=[DataRequired()])
    email      = StringField("Email", validators=[DataRequired(), Email()])
    phone      = StringField("Phone", validators=[Optional()])
    gender     = SelectField("Gender", choices=[("Male","Male"),("Female","Female")])
    dob        = DateField("Date of Birth", validators=[Optional()])
    nrc        = StringField("NRC", validators=[Optional()])
    address    = StringField("Address", validators=[Optional()])
    program_id = SelectField("Program", coerce=int, validators=[DataRequired()])
    submit     = SubmitField("Register")

class EvaluationForm(FlaskForm):
    lecturer_name = StringField("Lecturer Name", validators=[DataRequired()])
    knowledge    = IntegerField("Knowledge of subject (1-5)",   validators=[DataRequired(), NumberRange(1,5)])
    preparedness = IntegerField("Preparedness for class (1-5)", validators=[DataRequired(), NumberRange(1,5)])
    clarity      = IntegerField("Clarity of explanations (1-5)",validators=[DataRequired(), NumberRange(1,5)])
    punctuality  = IntegerField("Punctuality (1-5)",            validators=[DataRequired(), NumberRange(1,5)])
    engagement   = IntegerField("Student engagement (1-5)",     validators=[DataRequired(), NumberRange(1,5)])
    fairness     = IntegerField("Fairness of assessment (1-5)", validators=[DataRequired(), NumberRange(1,5)])
    overall      = IntegerField("Overall rating (1-5)",         validators=[DataRequired(), NumberRange(1,5)])
    comments     = TextAreaField("Comments to the lecturer", validators=[DataRequired()])
    submit       = SubmitField("Submit Evaluation")
