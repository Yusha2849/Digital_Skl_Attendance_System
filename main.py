from wtforms import BooleanField
from flask_bootstrap import Bootstrap5
from units.forms import Config, Login, ForgotPassword, ResetPassword, AddSecretaryForm, AddParentForm, AddStudentForm, GuardianForm, UpdateAttendanceForm, AddEducatorForm, ExemptionForm, GenerateClassListForm, ManageProfileForm, StudentAttendanceForm, DisplayForm
from flask import Flask, jsonify, redirect, session, url_for, request, flash, render_template, current_app, get_flashed_messages
from units import db, init_app, forms
from units.dao import AdminDAO, UserDAO, SecretaryDAO, EducatorDAO, GuardianDAO, SchoolClassDAO, StudentDAO, SchoolClassDAO, AttendanceRecordDAO, DatabaseUtilityDAO  #Added UserDAO for login
from units.models import Admin, Secretary, Educator, Guardian, Student, SchoolClass, AttendanceRecord
from units.student_attendance_tracker import MissingStudentIdentifier
from units.json_timestamp_manager import JSONTimestampManager
from units.overseer import Overseer  # Import from overseer.py
from units.missing_children_report import MissingStudentReport
from flask_login import login_user, logout_user, login_required, current_user
from units.utilities import save_config_data, is_configured, generate_username, role_required, generate_password, read_json_file, get_logged_in_parent_id#, update_grade_division_json, update_parent_json
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash

import os
import json
from datetime import timedelta, date, datetime

from werkzeug.security import generate_password_hash

app = Flask(__name__, instance_relative_config=True)
bootstrap = Bootstrap5(app)

def initialize_server():
    # Ensure the instance folder is created at the root level
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    # Configure the app to store the SQLite database in the root instance folder
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'project.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['SECRET_KEY'] = 'super secret string'
    
    # Initialize the database and import models
    init_app(app)

    # Create the database and tables if they do not exist
    with app.app_context():
        db.create_all()

    # Add a basic route
    return app
    

CONFIG_FILE = os.path.join(app.instance_path, 'app_config.json')
os.makedirs(app.instance_path, exist_ok=True)

app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = 'digitalattendance05@gmail.com'
app.config["MAIL_PASSWORD"] = 'mtrz tebu zxes feiy'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True    
mail = Mail(app) 


# General routes --------------------------------------------------------------------------------------------------
@app.route('/')
def home():
    if not is_configured():
        return redirect(url_for('setup'))
    return redirect(url_for('login'))

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if is_configured():
        return redirect(url_for('login'))
    
    form = Config()

    if form.validate_on_submit():
        email = form.email.data
        raw_password = form.password.data
        username = generate_username(email, 'admin')
        hashed_password = generate_password_hash(raw_password)

        school_name = form.school_name.data
        grade_range_start = form.grade_range_start.data
        grade_range_end = form.grade_range_end.data
        division_range_start = form.division_range_start.data
        division_range_end = form.division_range_end.data
        
        AdminDAO.add_admin(username=username, password=hashed_password, email=email)

        config_data = {
            'school_name': form.school_name.data,
            'grade_range': list(range(grade_range_start, grade_range_end + 1)),
            'division_range': [
                chr(i) for i in range(
                    ord(division_range_start.upper()), 
                    ord(division_range_end.upper()) + 1
                )
            ]
        }

        save_config_data(config_data)

        flash('Setup completed successfully. Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('config.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    if request.method == 'POST' and form.validate_on_submit(): # post code added from github
        username = form.username.data.strip()
        password = form.password.data

        user = UserDAO.get_user_by_username(username)

        if user:
            print(f"User found: {user.username}")
            if UserDAO.check_password(user, password):
                login_user(user)

                prefix = username[0].lower()
                session['user_type'] = prefix  # Store user role in the session

                # Store the guardian_id in session if the logged-in user is a parent
                if session['user_type'] == 'p':  # assuming 'p' is for parents
                    guardian = Guardian.query.filter_by(guardian_id=user.guardian_id).first()  # Adjust query to match your schema
                    if guardian:
                        session['guardian_id'] = guardian.guardian_id

                if prefix == 'a':
                    flash('Welcome Admin!', 'success')
                    return redirect(url_for('admin_dashboard'))
                elif prefix == 's':
                    flash('Welcome Secretary!', 'success')
                    return redirect(url_for('secretary_dashboard'))
                elif prefix == 'e':
                    flash('Welcome Educator!', 'success')
                    return redirect(url_for('educator_dashboard'))
                elif prefix == 'p':
                    flash('Welcome Parent!', 'success')
                    return redirect(url_for('parent_dashboard'))
                else:
                    flash('Unknown user type. Please contact support.', 'warning')
                    return redirect(url_for('login'))
            else:
                flash('Invalid username or password.', 'danger')
                print("Password incorrect.")
        else:
            flash('Invalid username or password.', 'danger')
            print("User not found.")

    return render_template('login.html', form=form)

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    forgot_form = ForgotPassword()
    if request.method == 'POST' and forgot_form.validate_on_submit():
        flash('Recovery email sent!', 'success') # Logic for reset password link is missing
        return redirect(url_for('login'))
    return render_template('forgot-user-pass.html', form=forgot_form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/manage_profile', methods=['GET', 'POST'])
@login_required
def manage_profile():
    manage_profile_form = ManageProfileForm()
    if request.method == 'POST' and manage_profile_form.validate_on_submit():
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('manage_profile'))
    return render_template('manage-profile.html', form=manage_profile_form)

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    change_password_form = ResetPassword()
    if request.method == 'POST' and change_password_form.validate_on_submit():
        flash('Password updated successfully!', 'success')
        return redirect(url_for('manage_profile'))
    return render_template('change-password.html', form=change_password_form)

@app.route('/admin/all', methods=['GET'])
def show_all_admins():
    admins = AdminDAO.get_all_admins()
    return render_template('admin-data.html', admins=admins)

@app.route('/student/all', methods=['GET'])
def show_all_students():
    students = StudentDAO.get_all_students()
    return render_template('student-data.html', students=students)

@app.route('/secretary/all', methods=['GET'])
def show_all_secretaries():
    secretaries = SecretaryDAO.get_all_secretaries()
    return render_template('secretary-data.html', secretaries=secretaries)

@app.route('/educator/all', methods=['GET'])
def show_all_educators():
    educators = EducatorDAO.get_all_educators()
    return render_template('educator-data.html', educators=educators)

@app.route('/guardian/all', methods=['GET', 'POST'])
def show_all_guardians():
    # Get the list of guardians from the database
    guardians = GuardianDAO.get_all_guardians()

    # Create a list of forms (one for each guardian)
    guardian_forms = {guardian.guardian_id: GuardianForm(obj=guardian) for guardian in guardians}

    if guardian_forms:
        # Handle form submissions for updates or deletes
        for guardian_id, form in guardian_forms.items():
            if form.validate_on_submit():
                if form.delete.data:
                    GuardianDAO.delete_guardian(guardian_id)
                    flash(f'Guardian with ID {guardian_id} deleted successfully!', 'success')
                    return redirect(url_for('show_all_guardians'))
                
    # Render the template, passing the guardians and the forms
    return render_template('parent-data.html', guardians=guardians, guardian_forms=guardian_forms)

@app.route('/school_class/all', methods=['GET'])
def show_all_classes():
    classes = SchoolClassDAO.get_all_classrooms()
    return render_template('class-data.html', classes=classes)


# Admin routes ----------------------------------------------------------------------------------------------------

@app.route('/admin_dashboard')
@role_required('a')  # Only admin users can access this page
def admin_dashboard():
    return render_template('admin-dashboard.html') 

@app.route('/add_secretary', methods=['GET', 'POST'])
@role_required('a')  # Assuming 'admin' is the role stored in session for admins
def add_secretary():
    form = AddSecretaryForm()

    if request.method == 'POST' and form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        rsa_id_num = form.rsa_id_num.data
        email = form.email.data
        cell_number = form.cell_number.data

        # Check if email, cell_number, or rsa_id_num already exists
        if SecretaryDAO.check_unique_fields(email, cell_number, rsa_id_num):
            flash('Error: Email, Cell Number, or RSA ID Number already exists in the system.', 'danger')
            return render_template('add-secretary.html', form=form)

        # If unique, proceed to create the secretary
        username = generate_username(email, 'secretary')
        password = generate_password()
        hashed_password = generate_password_hash(password)

        SecretaryDAO.add_secretary(
            first_name=first_name,
            last_name=last_name,
            rsa_id_num=rsa_id_num,
            email=email,
            cell_number=cell_number,
            username=username,
            password=hashed_password
        )

        # Create a welcome email for the new secretary
        msg = Message(subject="Welcome to the System - Your Account Details",
                      sender='digitalattendance05@gmail.com',
                      recipients=[email])
        msg.body = (f"Hello {first_name} {last_name},\n\n"
                    f"Your account has been created. Below are your login details:\n\n"
                    f"Username: {username}\n"
                    f"Password: {password} (Please change this after logging in)\n\n"
                    "Thank you.")
        mail.send(msg)

        flash('Secretary added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add-secretary.html', form=form)


@app.route('/add_educator', methods=['GET', 'POST'])
@role_required('a')
def add_educator():
    form = AddEducatorForm()

    if request.method == 'POST' and form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        rsa_id_num = form.rsa_id_num.data
        email = form.email.data
        cell_number = form.cell_number.data

        # Check if email, cell_number, or rsa_id_num already exists
        if EducatorDAO.check_unique_fields(email, cell_number, rsa_id_num):
            flash('Error: Email, Cell Number, or RSA ID Number already exists in the system.', 'danger')
            return render_template('add-educator.html', form=form)

        username = generate_username(email, 'educator')
        password = generate_password()
        hashed_password = generate_password_hash(password)

        EducatorDAO.add_educator(
            first_name=first_name,
            last_name=last_name,
            rsa_id_num=rsa_id_num,
            email=email,
            cell_number=cell_number,
            username=username,
            password=hashed_password
        )

        msg = Message(subject="Welcome to the System - Your Account Details",
                    sender='digitalattendance05@gmail.com',
                    recipients=[email])
        msg.body = (f"Hello {first_name} {last_name},\n\n"
                    f"Your account has been created. Below are your login details:\n\n"
                    f"Username: {username}\n"
                    f"Password: {password} (Please change this after logging in)\n\n"
                    "Thank you.")
        mail.send(msg)

        flash('Educator added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add-educator.html', form=form)

# Add a route to test DAO methods
# Ashlee See if this can be completed, use the dao file in units when doing this part
# This logic needs to be added to all db tables

@app.route('/secretaries', methods= ['GET'])
def getAllSec():
    sec = SecretaryDAO.get_all_secretaries()
    return jsonify([{
        'username' : secre.username,
        'email' : secre.email
    } for secre in sec])

@app.route('/students', methods=['GET'])
def get_all_students():
    students = StudentDAO.get_all_students()
    return jsonify([{
        'first_name': student.first_name,
        'last_name': student.last_name,
        'guardian_id': student.guardian_id
    } for student in students])

@app.route('/admins', methods=['GET'])
@login_required
def get_admins():
    if isinstance(current_user, Admin):
        admins = AdminDAO.get_all_admins()
        return jsonify([{"id": admin.admin_id, "username": admin.username} for admin in admins])
    else:
        return jsonify({"error": "Access forbidden"}), 403


# Secretary routes ------------------------------------------------------------------------------------------------
@app.route('/secretary_dashboard')
@role_required('s')
def secretary_dashboard():
    return render_template('secretary-dashboard.html')

@app.route('/add_class', methods=['GET', 'POST']) # the validation of 1 educator per a class needs to be implemented and not 2 of the same classes to be added
@role_required('s')
def add_class():
    form = forms.AddSchoolClass()

    config_data = read_json_file(CONFIG_FILE)
    grades = config_data.get('grade_range', [])
    divisions = config_data.get('division_range', [])

    # Populate form choices
    form.grade.choices = [(grade, f"Grade {grade}") for grade in grades]  # Convert grades to strings for display
    form.division.choices = [(division, division) for division in divisions]
    educators = Educator.query.all()
    form.educator.choices = [(educator.educator_id, educator.first_name) for educator in educators]

    if form.validate_on_submit():
        selected_grade = form.grade.data
        selected_division = form.division.data
        selected_educator_id = form.educator.data

        # Optionally, validate that the selected educator exists
        educator = Educator.query.get(selected_educator_id)
        if not educator:
            flash('Selected educator does not exist.')
            return redirect(url_for('add_class'))
        
        # Check if the class with the same grade and division already exists
        if SchoolClassDAO.check_unique_class(selected_grade, selected_division):
            flash('Error: Class with the same Grade and Division already exists.', 'danger')
            return redirect(url_for('add_class'))

        # Check if the educator is already allocated to another class
        if SchoolClassDAO.check_educator_allocation(selected_educator_id):
            flash('Error: Educator is already allocated to a class.', 'danger')
            return redirect(url_for('add_class'))

        # Initialize class_students as an empty dictionary/list
        class_students = []  # You can modify this based on your application's requirements {}

        try:
            SchoolClassDAO.add_class(
                educator_id=selected_educator_id,
                grade=selected_grade,
                division=selected_division,
                class_students=class_students
            )
            flash(f'Class Grade {selected_grade} Division {selected_division} added with teacher {educator.first_name}!')
            return redirect(url_for('secretary_dashboard'))  # Redirect to secretary_dashboard after success
        except Exception as e:
            # Handle exceptions (e.g., database errors)
            flash(f'An error occurred while adding the class: {str(e)}')
            return redirect(url_for('add_class'))

    return render_template('add_class.html', form=form)


@app.route('/add_parent', methods=['GET', 'POST'])
@role_required('s')
def add_parent():
    form = AddParentForm()  

    if request.method == 'POST' and form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        rsa_id_num = form.rsa_id_num.data
        email = form.email.data
        cell_number = form.cell_number.data
        address = f"{form.street_address.data}, {form.suburb.data}, {form.city.data}, {form.province.data}"

        # Check if email, cell_number, or rsa_id_num already exists
        if GuardianDAO.check_unique_fields(email, cell_number, rsa_id_num):
            flash('Error: Email, Cell Number, or RSA ID Number already exists in the system.', 'danger')
            return render_template('add-parent.html', form=form)

        username = generate_username(email, 'parent')
        password = generate_password()
        hashed_password = generate_password_hash(password)

        GuardianDAO.add_guardian(
            first_name=first_name,
            last_name=last_name,
            rsa_id_number=rsa_id_num,
            email=email,
            cell_number=cell_number,
            address=address,
            username=username,
            password=hashed_password
        )
        
        msg = Message(subject="Welcome to the System - Your Account Details",
                    sender='digitalattendance05@gmail.com',
                    recipients=[email])
        msg.body = (f"Hello {first_name} {last_name},\n\nYour account has been created. "
                    f"Below are your login details:\n\n"
                    f"Username: {username}\n"
                    f"Password: {password} (Please change this after logging in)\n\n"
                    "Thank you.")
        mail.send(msg)

        flash('Parent/Guardian added successfully!', 'success')
        return redirect(url_for('secretary_dashboard'))

    return render_template('add-parent.html', form=form)


@app.route('/add_student', methods=['GET', 'POST'])
@role_required('s')
def add_student():
    form = AddStudentForm()

    # Populate the guardian choices
    guardians = GuardianDAO.get_all_guardians()
    form.guardian_id.choices = [(guardian.guardian_id, f'{guardian.first_name} {guardian.last_name}') for guardian in guardians]

    classes = SchoolClass.query.all()
    form.class_choice.choices = [(school_class.class_id, f'Grade {school_class.grade} - {school_class.division}') for school_class in classes]

    if request.method == 'POST' and form.validate_on_submit():

        first_name = form.first_name.data
        last_name = form.last_name.data
        rsa_id_number = form.rsa_id_number.data
        selected_class = form.class_choice.data
        guardian_id = form.guardian_id.data

        # Check if email, cell_number, or rsa_id_num already exists
        if StudentDAO.check_unique_fields(rsa_id_number):
            flash('Error: RSA ID Number already exists in the system.', 'danger')
            return render_template('add-student.html', form=form)

        # Add the student to the Student table and retrieve the Student object
        new_student = StudentDAO.add_student(first_name, last_name, rsa_id_number, guardian_id)
        
        # Get the newly added student's ID
        if new_student:
            student_id = new_student.student_id
        else:
            raise Exception("Failed to add the student.")
        

        # Retrieve the selected guardian by ID
        selected_guardian = Guardian.query.get(guardian_id)
        new_dependants_list = selected_guardian.guardian_dependants_list.copy()
        new_dependants_list.append([student_id, selected_class])
        selected_guardian.guardian_dependants_list = new_dependants_list
        db.session.commit()

        # Retrieve the selected class by ID
        selected_class = SchoolClass.query.get(selected_class)
        new_class_students = selected_class.class_students.copy()
        new_class_students.append(student_id)
        selected_class.class_students = new_class_students
        db.session.commit()

        flash('Student added successfully!', 'success')
        return redirect(url_for('add_student')) # Currently going to display form again, can switch to display all students in student table

    return render_template('add-student.html', form=form)


@app.route('/update_attendance', methods=['GET', 'POST'])
def update_attendance():
    form = UpdateAttendanceForm()  # Ensure it's added in forms.py

    # 1. Populate Grade and Division dropdown
    form.class_name.choices = SchoolClassDAO.get_all_classes()

    # 2. Set the current date in the form
    form.date.data = datetime.now().strftime('%Y-%m-%d')  # Set the current date

    if request.method == 'POST' and form.validate_on_submit():
        # Your logic for updating attendance goes here
        # For example, saving data to the database
        # ...

        # Flash a success message
        flash('Attendance updated successfully.', 'success')

        # Redirect to secretary_dashboard after flashing the message
        return redirect(url_for('secretary_dashboard'))

    

    return render_template('update-attendance.html', form=form)

@app.route('/add_secretary_notice', methods=['GET', 'POST']) # Needs validation for the date options and syncing dropdown lists
@role_required('s')  # this function needs attention, the student choices need to update dynamically when a class is selected
def add_absentee_notice_secretary():
    form = ExemptionForm()

    # Step 1: Populate the 'class_info' dropdown with available classes
    classroom_choice = []
    classes = SchoolClass.query.all()  # Fetch all classes from the SchoolClass table

    for classroom in classes:
        class_id = classroom.class_id
        class_grade = classroom.grade
        class_div = classroom.division
        classroom_choice.append((class_id, f"Grade {class_grade} - {class_div}"))

    form.class_info.choices = classroom_choice

    # Check if the button to fetch students is pressed
    if request.method == 'POST':
        if 'fetch_students' in request.form:  # Check if fetch_students button was pressed
            selected_class_id = form.class_info.data
            # Fetch the students for the selected class
            students = Student.query.filter_by(class_id=selected_class_id).all()

            student_choices = []
            for student in students:
                student_id = student.student_id
                student_name = student.first_name  # Assuming 'first_name' is the column name
                student_choices.append((student_id, f"{student_name} (ID: {student_id})"))

            form.student_id.choices = student_choices
        elif form.validate_on_submit():  # Check if the submit button was pressed
            # Retrieve form data
            start_date = form.start_date.data
            end_date = form.end_date.data
            student_id = form.student_id.data
            class_id = form.class_info.data
            reason = form.reason.data

            # Step 3: Store the absentee notice in a JSON file
            notices_folder = os.path.join(current_app.instance_path, 'notices')
            if not os.path.exists(notices_folder):
                os.makedirs(notices_folder)

            # Define the path for the class-specific JSON file
            class_json_path = os.path.join(notices_folder, f"{class_id}.json")

            # Initialize the data structure
            date_list = {}

            # Check if the JSON file already exists
            if os.path.exists(class_json_path):
                with open(class_json_path, 'r') as f:
                    date_list = json.load(f)
            else:
                # Initialize an empty list if the file is new
                date_list = {}

            # Generate a list of dates from start_date to end_date
            current_date = start_date
            while current_date <= end_date:
                date_key = current_date.isoformat()  # Use ISO format as a key
                if date_key not in date_list:
                    date_list[date_key] = []  # Create a new list for this date

                # Append the student notice (id and reason) to the day's list
                date_list[date_key].append({
                    'student_id': student_id,
                    'reason': reason
                })
                current_date += timedelta(days=1)

            # Write the updated data back to the JSON file
            with open(class_json_path, 'w') as f:
                json.dump(date_list, f, indent=4)

            flash("Absentee notice submitted successfully!", "success")
            return render_template('secretary-dashboard.html')
    return render_template('add-secretary-notice.html', form=form)

# Define the path to the JSON file for storing timestamps


@app.route('/missing-students', methods=['GET', 'POST'])
def missing_students():
    with app.app_context():
        report = overseer.get_overdue_report()
        print(overseer.get_overdue_report())
        return render_template('missing-students.html', report=report)
    
@app.route('/display-student/<student_num>', methods=['GET', 'POST'])
def display_student(student_num):
    # Get the student and guardian information
    student = StudentDAO.get_student_by_id(student_num)
    guardian = GuardianDAO.get_guardian_by_id(student.guardian_id)

    # Pass the student and guardian info to the HTML template
    return render_template('display_student.html', 
                           student=student, 
                           guardian=guardian)

# Educator routes --------------------------------------------------------------------------------------------------
@app.route('/educator_dashboard')
@role_required('e')
def educator_dashboard():
    return render_template('educator-dashboard.html')

current_dir = os.path.dirname(os.path.abspath(__file__))
NOTICES_PATH = os.path.join(current_dir, 'instance', 'notices')

@app.route('/generate_class_list', methods=['GET', 'POST'])
def generate_class_list():
    form = GenerateClassListForm()
    
    # 1. Populate Grade and Division dropdown
    form.class_name.choices = SchoolClassDAO.get_all_classes()

    # 2. Set the current date in the form
    form.date.data = datetime.now().strftime('%Y-%m-%d')
    # print(form.validate_on_submit())
    # print(form.errors)
    if request.method == 'POST' and form.validate_on_submit():
        # 3. Extract class ID and query class info
        selected_class_id = form.class_name.data.split(' - ')[-1]
        class_info = SchoolClassDAO.get_class_by_id(selected_class_id)

        if class_info:
            class_id = class_info.class_id
            educator_id = class_info.educator_id

            # Populate educator info
            educator = EducatorDAO.get_educator_by_id(educator_id)
            if educator:
                form.educator.data = f"{educator.first_name} {educator.last_name}"

            # Get list of students for the class
            student_ids = class_info.class_students

            # 4. JSON file path and handling notifications
            json_file_path = os.path.join(NOTICES_PATH, f'{class_id}.json')
            notified_students = []

            # Check if the JSON file exists and read data
            if os.path.exists(json_file_path):
                try:
                    with open(json_file_path, 'r') as json_file:
                        notices_data = json.load(json_file)

                        # Check for the current date in JSON
                        current_date_str = form.date.data
                        if current_date_str in notices_data:
                            date_list = notices_data[current_date_str]

                            # Extract notified students for the current date
                            notified_students = [int(entry['student_id']) for entry in date_list]
                except json.JSONDecodeError:
                    flash('Error reading notification data.', 'danger')

            # 5. Populate the student attendance form
            for student_id in student_ids:
                # Fetch student details
                student = StudentDAO.get_student_by_id(student_id)

                if student:
                    
                    # Create student form
                    student_form = StudentAttendanceForm()
                    student_form.first_name.data = student.first_name
                    student_form.last_name.data = student.last_name

                    # Check if student was notified based on JSON
                    notified = '1' if student_id in notified_students else '0'
                    student_form.notified.data = notified  # Set notified status as '1' or '0'


                    # Set status based on whether the student was notified
                    if student_form.notified.data == '1':
                        student_form.status.data = 'Absent'  # If notified, mark as Absent
                    else:
                        student_form.status.data = 'Present'  # Otherwise, mark as Present

                    # Append the student form entry to the FieldList
                    form.students.append_entry(student_form)

                    print(f"Student: {student.first_name} {student.last_name}, Notified: {student_form.notified.data}, Status: {student_form.status.data}")

            # Submit Attendance button logic
            if form.submit_attendance.data:
                print("Submitting attendance...")
                attendance_record_dict = {}

                # Iterate through the student forms and extract data
                print(f"Length of student_ids: {len(student_ids)}, Length of form.students: {len(form.students)}")
                for student_form, student_id in zip(form.students, student_ids):
                    notified = int(student_form.notified.data)  # Boolean to 1/0
                    status = 1 if student_form.status.data == 'Present' else 0  # Present -> 1, Absent -> 0

                    # Append to attendance record list
                    #attendance_record_list.append([student_id,[notified, status]])
                    attendance_record_dict[student_id] = [notified, status]
                    print(f"Student ID: {student_id}, Notified: {notified}, Status: {status}")
                
                # 6. Add attendance record to the DB
                attendance_record_date_str = form.date.data  # '2024-10-08'
                attendance_record_date = datetime.strptime(attendance_record_date_str, '%Y-%m-%d').date()
                json_manager.update_timestamp

                AttendanceRecordDAO.add_attendance_record(
                    attendance_record_date=attendance_record_date,
                    attendance_record_list=attendance_record_dict,
                    class_id=class_id
                )

                flash('Attendance record submitted successfully!', 'success')
                return redirect(url_for('educator_dashboard'))
        
    return render_template('class-list.html', form=form)

# Parent routes ---------------------------------------------------------------------------------------------------
@app.route('/parent_dashboard')
@role_required('p') 
def parent_dashboard():
    return render_template('parent-dashboard.html') 
   

@app.route('/add_absentee_notice', methods=['GET', 'POST']) # This needs validating for the date options and syncing the dropdown lists, 
@role_required('p')
def add_absentee_notice():
    form = ExemptionForm()

    guardian_id = get_logged_in_parent_id()

    if guardian_id:
        guardian = Guardian.query.filter_by(guardian_id=guardian_id).first() # Step 2: Query the Guardian table for the dependents list

        if guardian:
            # Step 3: Extract student_id and class_id from the dependants list
            dependants_list = guardian.guardian_dependants_list  # assuming this is a list of tuples [(student_id, class_id), ...]

            # Step 4: Populate the 'student_id' & 'class_info' dropdown
            student_choices = []
            classroom_choice = []
            for dep in dependants_list:
                student_id = dep[0]
                class_id = dep[1]
                student = Student.query.filter_by(student_id=student_id).first()  # Fetch the student record
                classroom = SchoolClass.query.filter_by(class_id=class_id).first()

                if student:
                    student_name = student.first_name  # Assuming 'first_name' is the column name
                    student_choices.append((student_id, f"{student_name} (ID: {student_id}, Class ID: {class_id})"))

                    class_grade = classroom.grade
                    class_div = classroom.division
                    classroom_choice.append((class_id, f"Grade {class_grade} - {class_div}"))
            
            form.student_id.choices = student_choices
            form.class_info.choices = classroom_choice
        else:
            flash("Guardian not found.", "danger")
    else:
        flash("No guardian ID found in session.", "danger")

    if request.method == 'POST' and form.validate_on_submit():
            # Retrieve form data
            start_date = form.start_date.data
            end_date = form.end_date.data
            student_id = form.student_id.data
            class_id = form.class_info.data
            reason = form.reason.data

            # Step 5: Store the absentee notice in a JSON file
            notices_folder = os.path.join(current_app.instance_path, 'notices')
            if not os.path.exists(notices_folder):
                os.makedirs(notices_folder)

             # Define the path for the class-specific JSON file
            class_json_path = os.path.join(notices_folder, f"{class_id}.json")

            # Initialize the data structure
            date_list = {}
            
            # Check if the JSON file already exists
            if os.path.exists(class_json_path):
                with open(class_json_path, 'r') as f:
                    date_list = json.load(f)
            else:
                # Initialize empty list if the file is new
                date_list = {}

            # Generate a list of dates from start_date to end_date
            current_date = start_date
            while current_date <= end_date:
                date_key = current_date.isoformat()  # Use ISO format as a key
                if date_key not in date_list:
                    date_list[date_key] = []  # Create a new list for this date
                
                # Append the student notice (id and reason) to the day's list
                date_list[date_key].append({
                    'student_id': student_id,
                    'reason': reason
                })
                current_date += timedelta(days=1)

            # Write the updated data back to the JSON file
            with open(class_json_path, 'w') as f:
                json.dump(date_list, f, indent=4)

            flash("Absentee notice submitted successfully!", "success")


    return render_template('add-attendance-exemption.html', form=form)

students = [
    {'first_name': 'John', 'last_name': 'Doe', 'grade': 'A', 'division': '1', 'cell_number': '123-456-7890'},
    {'first_name': 'Jane', 'last_name': 'Smith', 'grade': 'B', 'division': '2', 'cell_number': '987-654-3210'},
    {'first_name': 'Alice', 'last_name': 'Johnson', 'grade': 'A', 'division': '1', 'cell_number': '555-444-3333'},
]

@app.route('/missing', methods=['GET', 'POST'])
def missing():
    form = DisplayForm()
    
    if form.validate_on_submit():  # Check if the form is submitted
        return render_template('false-missing.html', form=form, students=students)  # Pass data to the template

    return render_template('false-missing.html', form=form, students=None)  # Show the form but no data yet

if __name__ == "__main__":
    app = initialize_server()
    
    with app.app_context():
        TIMESTAMP_FILE_PATH = os.path.join(app.instance_path, 'timestamps.json')
        #DatabaseUtilityDAO.execute_sql_script("static/script.sql")

        # Initialize your components
        json_manager = JSONTimestampManager(file_path=TIMESTAMP_FILE_PATH)
        attendance_dao = AttendanceRecordDAO  # Assuming you have a DB connection setup
        report_generator = MissingStudentReport()

        # Initialize the Overseer class and start the process
        overseer = Overseer(json_manager=json_manager, dao=attendance_dao, report_generator=report_generator,app=app)
        overseer.start()
        app.run(debug=True)

#     |'-.--._ _________:
#     |  /    |  __    __\
#     | |  _  | [\_\= [\_\
#     | |.' '. \.........|
#     | ( <)  ||:       :|_
#     \ '._.' | :.....: |_(o
#       '-\_   \ .------./
#       _   \   ||.---.||  _
#      / \  '-._|/\n~~\n' | \
#     (| []=.--[===[()]===[) |
#     <\_/  \_______/ _.' /_/
#     ///            (_/_/
#     |\\            [\\
#     ||:|           | I|
#     |::|           | I|
#     ||:|           | I|
#     ||:|           : \:
#     |\:|            \I|
#     :/\:            ([])
#     ([])             [|
#      ||              |\_
#     _/_\_            [ -'-.__
#    <]   \>            \_____.>
#      \__/