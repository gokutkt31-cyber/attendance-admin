from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField, FloatField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('employee', 'Employee'), ('hr', 'HR Manager'), ('admin', 'System Admin')], default='employee')
    
    # Employee Details
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    phone = StringField('Phone Number', validators=[Length(max=20)])
    designation = StringField('Designation', validators=[Length(max=100)])
    department_id = SelectField('Department', coerce=int, choices=[])
    
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please choose a different one.')

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Length(max=20)])
    designation = StringField('Designation', validators=[Length(max=100)])
    submit = SubmitField('Update Profile')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class DepartmentForm(FlaskForm):
    name = StringField('Department Name', validators=[DataRequired(), Length(max=100)])
    code = StringField('Department Code', validators=[DataRequired(), Length(max=20)])
    description = TextAreaField('Description')
    submit = SubmitField('Save')

class LeaveApplicationForm(FlaskForm):
    leave_type = SelectField('Leave Type', choices=[
        ('Casual', 'Casual Leave'),
        ('Medical', 'Medical Leave'),
        ('Earned', 'Earned Leave'),
        ('Maternity', 'Maternity Leave'),
        ('Paternity', 'Paternity Leave')
    ], validators=[DataRequired()])
    start_date = StringField('Start Date (YYYY-MM-DD)', validators=[DataRequired()])
    end_date = StringField('End Date (YYYY-MM-DD)', validators=[DataRequired()])
    reason = TextAreaField('Reason for Leave', validators=[DataRequired()])
    submit = SubmitField('Apply')

class SystemSettingsForm(FlaskForm):
    check_in_start_time = StringField('Shift Check-in Start Time (HH:MM:SS)', validators=[DataRequired()])
    check_in_grace_period_mins = IntegerField('Grace Period (Minutes)', validators=[DataRequired()])
    allowed_gps_latitude = FloatField('Office Latitude', validators=[DataRequired()])
    allowed_gps_longitude = FloatField('Office Longitude', validators=[DataRequired()])
    allowed_gps_radius_meters = FloatField('Allowed Proximity Radius (Meters)', validators=[DataRequired()])
    submit = SubmitField('Save Settings')
