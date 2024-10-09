from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, SubmitField, PasswordField, StringField, validators, EmailField, DateField, SelectField, HiddenField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import BooleanField, TextAreaField
from wtforms.validators import EqualTo, DataRequired, Email, Length, Regexp, NumberRange
from datetime import date

class Config(FlaskForm):
    email = EmailField('Email', validators=[validators.Email(), validators.DataRequired()], render_kw={"placeholder": "Enter your email"})
    password = PasswordField('Password', validators=[validators.DataRequired()], render_kw={"placeholder": "Create a password"})
    confirm_password = PasswordField('Confirm Password', validators=[
        validators.DataRequired(),
        EqualTo('password', message='Passwords must match')], render_kw={"placeholder": "Confirm your password"})
    
    school_name = StringField('School Name', validators=[DataRequired()], render_kw={"placeholder": "Enter school name"})
 
    grade_range_start = IntegerField(
        'Grade Range Start',
        validators=[DataRequired(), NumberRange(min=0, max=12)],
        render_kw={"placeholder": "Enter Lowest Grade "}

    )
    grade_range_end = IntegerField(
        'Grade Range End',
        validators=[DataRequired(), NumberRange(min=0, max=12)],
        render_kw={"placeholder": "Enter Highest Grade"}
    )
    division_range_start = StringField(
        'Division Range Start',
        validators=[DataRequired(), Length(min=1, max=1)],
        render_kw={"placeholder": "Enter Division Start"}

    )
    division_range_end = StringField(
        'Division Range End',
        validators=[DataRequired(), Length(min=1, max=1)],
                render_kw={"placeholder": "Enter Division End"}
    )
    submit = SubmitField('Submit')


class GuardianForm(FlaskForm):
    guardian_id = HiddenField()  # Hidden field to hold guardian ID
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    update = SubmitField('Update')
    delete = SubmitField('Delete')

class Login(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Enter your username"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Enter your password"})
    login = SubmitField('Login')


class ForgotPassword(FlaskForm):
    email = EmailField('Email', validators=[validators.Email(), validators.DataRequired()], render_kw={"placeholder": "Enter your email"})
    submit = SubmitField('Submit')

class AddEducatorForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Regexp(r'^[A-Za-z]+$', message='First name must contain only letters')], render_kw={"placeholder": "Enter your First Name"})
    last_name = StringField('Last Name', validators=[DataRequired(), Regexp(r'^[A-Za-z]+$', message='Last name must contain only letters')], render_kw={"placeholder": "Enter your Last Name"})
    rsa_id_num = StringField(
        'RSA ID Number', 
        validators=[
            DataRequired(), 
            Regexp(r'^\d{13}$', message='RSA ID must be exactly 13 digits')
        ], 
        render_kw={"placeholder": "Enter your ID Number"}
    ) 
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Enter your email"})
    cell_number = StringField(
        'Cell Number', 
        validators=[
            DataRequired(), 
            Regexp(r'^\d{10}$', message='Cell number must be exactly 10 digits')
        ], 
        render_kw={"placeholder": "Enter your Cell Number"}
    )
    add_educator = SubmitField('Add Educator')     

class ResetPassword(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(), 
        Length(min=8, message='Password must be at least 8 characters long')
    ], render_kw={"placeholder": "Enter new password"})
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ], render_kw={"placeholder": "Confirm new password"})
    
    # If you have some sort of agreement confirmation
    confirm = BooleanField('Confirm', validators=[DataRequired()])
    
    submit = SubmitField('Submit')

class AddSecretaryForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=30), Regexp(r'^[A-Za-z]+$', message='First name must contain only letters')], render_kw={"placeholder": "Enter your First Name"})
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=30), Regexp(r'^[A-Za-z]+$', message='Last name must contain only letters')], render_kw={"placeholder": "Enter your Last Name"})
    rsa_id_num = StringField('RSA ID Number', validators=[
        DataRequired(), 
        Regexp(r'^\d{13}$', message='RSA ID must be exactly 13 digits')
    ], render_kw={"placeholder": "Enter your ID Number"})
    email = EmailField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Enter your Email"})
    cell_number = StringField('Cell Number', validators=[
        DataRequired(), 
        Regexp(r'^\d{10}$', message='Cell number must be exactly 10 digits')
    ], render_kw={"placeholder": "Enter your Cell Number"})
    submit = SubmitField('Add Secretary')

class ManageProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Regexp(r'^[A-Za-z]+$', message='Username must contain only letters')], render_kw={"placeholder": "Enter your username"})
    email = StringField('Email', validators=[DataRequired()], render_kw={"placeholder": "Enter your email"})
    update_profile = SubmitField('Edit Details')

class AddParentForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50), Regexp(r'^[A-Za-z]+$', message='First name must contain only letters')], render_kw={"placeholder": "Enter your First Name"})
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50), Regexp(r'^[A-Za-z]+$', message='Last name must contain only letters')], render_kw={"placeholder": "Enter your Last Name"})
    rsa_id_num = StringField('RSA ID Number', validators=[
        DataRequired(), 
        Regexp(r'^\d{13}$', message='RSA ID must be exactly 13 digits')
    ], render_kw={"placeholder": "Enter your ID Number"})
    email = EmailField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Enter your Email"})
    cell_number = StringField('Cell Number', validators=[
        DataRequired(), 
        Regexp(r'^\d{10}$', message='Cell number must be exactly 10 digits')
    ], render_kw={"placeholder": "Enter your Cell Number"})

    street_address = StringField('Street Address', validators=[DataRequired(), Length(min=5, max=100)], render_kw={"placeholder": "Enter your Street Address"})
    suburb = StringField('Suburb', validators=[DataRequired(), Length(min=2, max=50)], render_kw={"placeholder": "Enter your suburb"})
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=50)], render_kw={"placeholder": "Enter your City"})
    province = SelectField('Province', choices=[
        ('Gauteng', 'Gauteng'),
        ('Western Cape', 'Western Cape'),
        ('KwaZulu-Natal', 'KwaZulu-Natal'),
        ('Eastern Cape', 'Eastern Cape'),
        ('Free State', 'Free State'),
        ('Limpopo', 'Limpopo'),
        ('Mpumalanga', 'Mpumalanga'),
        ('Northern Cape', 'Northern Cape'),
        ('North West', 'North West')
    ], validators=[DataRequired()], render_kw={"placeholder": "Select your province"})

    submit = SubmitField('Add Parent')


class AddStudentForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)], render_kw={"placeholder": "Enter your First Name"})
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)], render_kw={"placeholder": "Enter your Last Name"})
    rsa_id_number = StringField('RSA ID Number', validators=[
        DataRequired(), 
        Regexp(r'^\d{13}$', message='RSA ID must be exactly 13 digits')
    ], render_kw={"placeholder": "Enter your ID Number"})
    guardian_id = SelectField('Guardian', choices=[], coerce=int, validators=[DataRequired()], render_kw={"placeholder": "Guardian Name"})
    class_choice = SelectField('Grade and Division', 
        choices=[], 
        coerce=int, 
        validators=[DataRequired()], 
        render_kw={"placeholder": "Select Grade and Division"}
    )
    submit = SubmitField('Add Student')

# Check this code
class AddSchoolClass(FlaskForm):
    educator = SelectField('Educator', choices=[], validators=[DataRequired()])
    grade = SelectField('Grade', choices=[], validators=[DataRequired()])
    division = SelectField('Division', choices=[], validators=[DataRequired()])
    submit = SubmitField('Add Class')
    

class UpdateAttendanceForm(FlaskForm):
    date = StringField('Date', default=date.today().isoformat(), render_kw={"readonly": True})
    class_name = SelectField('Class', choices=[], validators=[DataRequired()], render_kw={"placeholder": "Select Class"})
    student_id = SelectField('Student ID', choices=[('James Adam', 'James Adam'), ('Paul Tim', 'Paul Tim')], validators=[DataRequired()], render_kw={"placeholder": "Student ID Number"})
    attendance_status = SelectField('Attendance Status', choices=[('Present', 'Present'), ('Absent', 'Absent')], default='Absent')
    update_attendance = SubmitField('Update Attendance')
    
class ExemptionForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    class_info = SelectField('Class', validators=[DataRequired()])
    student_id = SelectField('Student ID', choices=[('James Adam', 'James Adam'), ('Paul Tim', 'Paul Tim')], validators=[DataRequired()], id='student-dropdown')
    reason = TextAreaField('Reason for Exemption', validators=[DataRequired()], id='class-info-dropdown')
    submit = SubmitField('Notify School')

class StudentAttendanceForm(FlaskForm):
    first_name = StringField('First Name', render_kw={"readonly": True})
    last_name = StringField('Last Name', render_kw={"readonly": True})
    notified = SelectField('Notified', choices=[('1', 'Yes'), ('0', 'No')], default='0')
    status = SelectField('Status', choices=[('Present', 'Present'), ('Absent', 'Absent')])

    class Meta:
        csrf = False  # Disable CSRF for this nested form

class GenerateClassListForm(FlaskForm):
    date = StringField('Date', default=date.today().isoformat(), render_kw={"readonly": True})
    class_name = SelectField('Class', choices=[], validators=[DataRequired()], render_kw={"placeholder": "Select Class"})
    educator = StringField('Form Educator', render_kw={"readonly": True})

    # Fields for the student list
    students = FieldList(FormField(StudentAttendanceForm))  # For listing students dynamically
    
    # Two action buttons
    generate = SubmitField('Generate List')
    submit_attendance = SubmitField('Submit Attendance')


class DisplayForm(FlaskForm):
    display_button = SubmitField('Display Students')