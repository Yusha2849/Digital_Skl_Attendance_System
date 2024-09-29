<<<<<<< HEAD
from flask import Flask, jsonify, redirect, url_for, request, flash, render_template
from units import db, init_app
from units.dao import AdminDAO, UserDAO, DatabaseUtilityDAO  # Added UserDAO for login
from flask_login import login_user, logout_user, login_required, current_user
import os

app = Flask(__name__, instance_relative_config=True)

def initialize_server():
=======
import os
import string

import json

from flask import Flask, jsonify, render_template, redirect, url_for, flash, request
from units import db, init_app, forms
from units.dao import AdminDAO
from units.models import Admin
from units.utilities import save_config_data, is_configured, generate_username#, generate_password, update_grade_division_json, update_parent_json
from flask_mail import Mail, Message
from dotenv import load_dotenv
from random import *

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, instance_relative_config=True)

def create_app():
    
>>>>>>> backend/admin_func
    # Ensure the instance folder is created at the root level
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    # Configure the app to store the SQLite database in the root instance folder
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'project.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
<<<<<<< HEAD
    app.secret_key = 'super secret string'
=======
    app.config['SECRET_KEY'] = 'f3b1e2d4c5a69788b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5g6h7i8j9k0l1m2'
>>>>>>> backend/admin_func
    
    # Initialize the database and import models
    init_app(app)

    # Create the database and tables if they do not exist
    with app.app_context():
        db.create_all()

<<<<<<< HEAD
    return app

@app.route('/')
def home():
    if current_user.is_authenticated:
        return f"<h1>Welcome, {current_user.username}</h1>"
    return "<h1>Welcome, Guest</h1>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
=======
    # Add a basic route
    return app
    

CONFIG_FILE = os.path.join(app.instance_path, 'app_config.json')
os.makedirs(app.instance_path, exist_ok=True)



app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = os.getenv('ATTENDANCE_EMAIL') # digitalattendance05@gmail.com
app.config["MAIL_PASSWORD"] = os.getenv('ATTENDANCE_EMAIL_PASS') # mtrz tebu zxes feiy
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
    
    form = forms.Config()

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

    form = forms.Login()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        prefix = username[0]
        user = None

        if prefix == 'a':
            user = AdminDAO.query.filter_by(username=username).first()
        #elif prefix == 's':
        #    user = Secretaries.query.filter_by(username=username).first()
        #elif prefix == 'p':
        #    user = Parents.query.filter_by(username=username).first()
        #elif prefix == 'e':
        #    user = Educator.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            #session['user_id'] = user.id
            #session['user_type'] = prefix

            if prefix == 'a':
                return redirect(url_for('admin_dashboard'))
            elif prefix == 'p':
                return redirect(url_for('parent_dashboard'))
            elif prefix == 's':
                return redirect(url_for('secretary_dashboard'))
            elif prefix == 'e':
                return redirect(url_for('educator_dashboard'))
        else:
            flash("Invalid username or password", "danger")    
    return render_template('login.html', form = form)

'''


@app.route('/manage_profile', methods=['GET', 'POST'])
@login_required
def manage_profile():
    username = current_user.username
    role = None
    user = None

    if username.startswith('a'):
        user = Admin.query.filter_by(username=username).first()
        role = 'admin'
    elif username.startswith('s'):
        user = Secretary.query.filter_by(username=username).first()
        role = 'secretary'
    elif username.startswith('e'):
        user = Educator.query.filter_by(username=username).first()
        role = 'educator'
    elif username.startswith('p'):
        user = Parent.query.filter_by(username=username).first()
        role = 'parent'
    else:
        flash('Invalid user role or username', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':

        if 'change_password' in request.form:
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if not check_password_hash(user.password, current_password):
                flash("Current password is incorrect", "danger")

            elif new_password != confirm_password:
                flash("New password and confirmation don't match", "danger")

            else:
                user.password = generate_password_hash(new_password)
                flash("Password updated successfully", "success")
                db.session.commit()

        if 'update_mobile' in request.form and role in ['secretary', 'educator', 'parent']:
            new_mobile_number = request.form.get('mobile_number')
            user.mobile_number = new_mobile_number
            flash("Mobile number updated successfully", "success")
            db.session.commit()

        return redirect(url_for('manage_profile'))

    return render_template('manage_profile.html', user=user, role=role)

@app.route('/update_attendance', methods=['GET', 'POST'])
def update_attendance():
    form = forms.UpdateAttendanceForm()

    form.grade.choices = [(grade.id, grade.name) for grade in Grades.query.all()]
    form.division.choices = [(division.id, division.name) for division in Divisions.query.all()]

    if request.method == 'POST' and form.grade.data and form.division.data:
        class_id = f"{form.grade.data}{form.division.data}"
        students = Students.query.filter_by(grade=form.grade.data, division=form.division.data).all()
        form.student_id.choices = [(student.id, f"{student.first_name} {student.last_name}") for student in students]
>>>>>>> backend/admin_func
        
        # Use the DAO to get the user and check password
        user = UserDAO.get_user_by_username(username)

        if user and UserDAO.check_password(user, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')

<<<<<<< HEAD
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Add a route to test DAO methods
@app.route('/admins', methods=['GET'])
@login_required
def get_admins():
    if isinstance(current_user, Admin):
        admins = AdminDAO.get_all_admins()
        return jsonify([{"id": admin.admin_id, "username": admin.admin_username} for admin in admins])
    else:
        return jsonify({"error": "Access forbidden"}), 403
=======
def mark_attendance(date, class_id):
    filepath = os.path.join('attendance_records', f"{date}_{class_id}_attendance.json")
    
    if not os.path.exists(filepath):
        flash('Attendance register not found.', 'danger')
        return redirect(url_for('generate_class_list'))

    # Load the existing attendance data
    with open(filepath, 'r') as file:
        attendance_data = json.load(file)

    form = MarkAttendanceForm()
    
    # Pre-populate attendance form with student information
    for student_record in attendance_data:
        student_id = student_record['student_id']
        form.attendance_statuses.append_entry({
            'student_id': student_id,
            'first_name': student_record['first_name'],
            'last_name': student_record['last_name'],
            'exemption_status': student_record.get('exemption_status', ''),
            'attendance_status': student_record['attendance_status']
        })
    
    if form.validate_on_submit():
        # Update the attendance based on form inputs
        for idx, field in enumerate(form.attendance_statuses):
            student_record = attendance_data[idx]
            student_record['attendance_status'] = field.attendance_status.data
        
        # Save updated attendance data
        with open(filepath, 'w') as file:
            json.dump(attendance_data, file, indent=4)
        
        flash('Register submitted successfully!', 'success')
        return redirect(url_for('educator_dashboard'))

    # Get the class and form educator details
    class_info = Class.query.filter_by(id=class_id).first()
    form_educator = class_info.form_educator

    return render_template('mark_attendance.html', form=form, date=date, grade=class_info.grade, division=class_info.division, form_educator=form_educator)
   
@app.route('/generate_class_list', methods=['GET', 'POST'])
def generate_class_list():
    form = forms.GenerateClassListForm()

    # Populate Grade and Division dropdowns
    form.grade.choices = [(grade.id, grade.name) for grade in Grades.query.all()]
    form.division.choices = [(division.id, division.name) for division in Divisions.query.all()]

    if form.validate_on_submit():
        date = form.date.data
        grade = form.grade.data
        division = form.division.data

        # Generate class list based on selected Grade and Division
        class_id = f"{grade}{division}"
        class_info = Class.query.filter_by(grade=grade, division=division).first()
        
        # Fetch form educator for the class
        form_educator = class_info.form_educator

        # Generate attendance register for the day (create JSON if not exists)
        date_str = date.strftime('%Y-%m-%d')
        filename = f"{date_str}_{class_id}_attendance.json"
        filepath = os.path.join('attendance_records', filename)

        if os.path.exists(filepath):
            with open(filepath, 'r') as file:
                attendance_data = json.load(file)
        else:
            # Create a new register for the class
            attendance_data = generate_daily_attendance(date, grade, division)

            # Save it to a JSON file
            with open(filepath, 'w') as file:
                json.dump(attendance_data, file, indent=4)

        # Redirect to the class list page to mark attendance
        return redirect(url_for('mark_attendance', date=date_str, class_id=class_id))

    return render_template('generate_class_list.html', form=form)

@app.route('/add_attendance_exemption', methods=['GET', 'POST'])
def add_attendance_exemption():
    form = ExemptionForm()

    form.grade.choices = [(grade.id, grade.name) for grade in Grades.query.all()]
    form.division.choices = [(division.id, division.name) for division in Divisions.query.all()]

    if form.grade.data and form.division.data:
        form.student_id.choices = [(student.id, f"{student.first_name} {student.last_name}") 
                                   for student in Students.query.filter_by(grade=form.grade.data, division=form.division.data).all()]

    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        grade = form.grade.data
        division = form.division.data
        student_id = form.student_id.data
        reason = form.reason.data

        student = Students.query.get(student_id)
        class_id = f"{grade}{division}"

        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            filename = f"{date_str}_{class_id}_attendance.json"
            filepath = os.path.join('attendance_records', filename)

            if os.path.exists(filepath):
                with open(filepath, 'r') as file:
                    attendance_data = json.load(file)
            else:
                attendance_data = generate_daily_attendance(current_date, grade, division)

            for student_record in attendance_data:
                if student_record['student_id'] == student_id:
                    student_record['attendance_status'] = 'Exempted'
                    student_record['exemption_status'] = reason
                    break

            with open(filepath, 'w') as file:
                json.dump(attendance_data, file, indent=4)

            current_date += timedelta(days=1)

        flash('Exemption successfully added.', 'success')
        return redirect(url_for('secretary_dashboard'))

    return render_template('add_attendance_exemption.html', form=form)

def generate_daily_attendance(date, grade, division):
    class_id = f"{grade}{division}"
    filename = f"{date}_{class_id}_attendance.json"
    filepath = os.path.join('attendance_records', filename)

    if not os.path.exists(filepath):
        students = Students.query.filter_by(grade=grade, division=division).all()
        attendance_data = []

        for student in students:
            attendance_data.append({
                'student_id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'attendance_status': 'Absent',
                'exemption_status': 'None'
            })

        with open(filepath, 'w') as file:
            json.dump(attendance_data, file, indent=4)

    return filepath

    
# Admin routes ----------------------------------------------------------------------------------------------------
@app.route('/admins', methods=['GET'])
def get_admins():
    admins = AdminDAO.get_all_admins()
    return jsonify([{"id": admin.admin_id, "username": admin.admin_username} for admin in admins])

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_type' in session and session['user_type'] == 'a':
        return render_template('admin_dashboard.html')
    else:
        return redirect(url_for('login'))

    #azb5499: THIS FUNCTION NEEDS TO CHANGE,INCORRECT CODE. 


# Secretary routes ------------------------------------------------------------------------------------------------
@app.route('/add_secretary', methods=['GET', 'POST'])
def add_secretary():
    if 'user_type' in session and session['user_type'] == 'a':
        #azb5499: PROPER VERIFICATION NEEDS TO BE HERE. WILL BE FIXED LATER
        form = AddSecretaryForm()

        if form.validate_on_submit():
            first_name = form.first_name.data
            last_name = form.last_name.data
            rsa_id_num = form.rsa_id_num.data
            email = form.email.data
            cell_number = form.cell_number.data

            username = generate_username(email, 'secretary')
            password = generate_password()
            hashed_password = generate_password_hash(password)

            new_secretary = Secretaries(
                first_name=first_name,
                last_name=last_name,
                RSA_id_num=rsa_id_num,
                email=email,
                cell_number=cell_number,
                username=username,
                password=hashed_password
            )

            db.session.add(new_secretary)
            db.session.commit()

            # azb5499: This logic will be added later with database functionality

            msg = Message(subject="Welcome to the System - Your Account Details",
                        sender='digitalattendance05@gmail.com',
                        recipients=[email])
            msg.body = (f"Hello {first_name} {last_name},\n\n"
                        f"Your account has been created. Below are your login details:\n\n"
                        f"Username: {username}\n"
                        f"Password: {password} (Please change this after logging in)\n\n"
                        "Thank you.")
            mail.send(msg)

            flash('Secretary successfully added and email sent.', 'success')
            return redirect(url_for('admin_dashboard'))

        return render_template('add_secretary.html', form=form)
    else:
        flash("You must be an admin to access this page.", 'danger')
        return redirect(url_for('login'))

@app.route('/secretary_dashboard')
def secretary_dashboard():
    if 'user_type' in session and session['user_type'] == 's':
        return render_template('secretary_dashboard.html')
    else:
        return redirect(url_for('login'))


# Educator routes --------------------------------------------------------------------------------------------------
@app.route('/add_educator', methods=['GET', 'POST'])
def add_educator():
    if 'user_type' in session and session['user_type'] == 'a':
        form = AddEducatorForm()

        if form.validate_on_submit():
            first_name = form.first_name.data
            last_name = form.last_name.data
            rsa_id_num = form.rsa_id_num.data
            email = form.email.data
            cell_number = form.cell_number.data

            username = generate_username(email, 'educator')
            password = generate_password()
            hashed_password = generate_password_hash(password)

            new_educator = Educators(
                first_name=first_name,
                last_name=last_name,
                RSA_id_num=rsa_id_num,
                email=email,
                cell_number=cell_number,
                username=username,
                password=hashed_password
            )

            db.session.add(new_educator)
            db.session.commit()

            #azb5499: This will be added in a future update
            msg = Message(subject="Welcome to the System - Your Account Details",
                        sender='digitalattendance05@gmail.com',
                        recipients=[email])
            msg.body = (f"Hello {first_name} {last_name},\n\n"
                        f"Your account has been created. Below are your login details:\n\n"
                        f"Username: {username}\n"
                        f"Password: {password} (Please change this after logging in)\n\n"
                        "Thank you.")
            mail.send(msg)

            flash('Educator successfully added and email sent.', 'success')
            return redirect(url_for('admin_dashboard'))

        return render_template('add_educator.html', form=form)
    else:
        flash("You must be an admin to access this page.", 'danger')
        return redirect(url_for('login'))

@app.route('/educator_dashboard')
def educator_dashboard():
    if 'user_type' in session and session['user_type'] == 'e':
        return render_template('educator_dashboard.html')
    else:
        return redirect(url_for('login'))


 #@app.route('/mark_attendance/<date>/<class_id>', methods=['GET', 'POST'])


# Parent routes ---------------------------------------------------------------------------------------------------
@app.route('/add_parent', methods=['GET', 'POST'])
def add_parent():
    if 'user_type' in session and session['user_type'] == 's':
        form = AddParentForm()  

        if form.validate_on_submit():
            first_name = form.first_name.data
            last_name = form.last_name.data
            rsa_id_num = form.rsa_id_num.data
            email = form.email.data
            cell_number = form.cell_number.data
            address = f"{form.street_address.data}, {form.suburb.data}, {form.city.data}, {form.province.data}"


            username = generate_username(email, 'parent')
            password = generate_password()
            hashed_password = generate_password_hash(password)

            new_parent = Parents(
                first_name=first_name,
                last_name=last_name,
                RSA_id_num=rsa_id_num,
                email=email,
                cell_number=cell_number,
                address=address,
                username=username,
                password=hashed_password
            )

            db.session.add(new_parent)
            db.session.commit()
            
            msg = Message(subject="Welcome to the System - Your Account Details",
                        sender='digitalattendance05@gmail.com',
                        recipients=[email])
            msg.body = (f"Hello {first_name} {last_name},\n\nYour account has been created. "
                        f"Below are your login details:\n\n"
                        f"Username: {username}\n"
                        f"Password: {password} (Please change this after logging in)\n\n"
                        "Thank you.")
            mail.send(msg)

            flash('Parent successfully added and email sent.', 'success')
            return redirect(url_for('secretery_dashboard'))

        return render_template('add_parent.html', form=form)

    else:
        flash('You are not authorized to view this page.', 'danger')
        return redirect(url_for('login'))

# Student routes --------------------------------------------------------------------------------------------------
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if 'user_type' in session and session['user_type'] == 's':
        form = forms.AddStudentForm()

        form.grade.choices = [(str(grade), str(grade)) for grade in config['grade_range']]
        form.division.choices = [(division, division) for division in config['division_range']]
        form.guardian.choices = [(p.id, f"{p.first_name} {p.last_name}") for p in Parents.query.all()]

        if form.validate_on_submit():
            first_name = form.first_name.data
            last_name = form.last_name.data
            id_num = form.id_num.data
            guardian_id = form.guardian.data
            grade_id = form.grade.data
            division_id = form.division.data

            class_row = Class.query.filter_by(grade_id=grade_id, division_id=division_id).first()

            if not class_row:
                flash('Error: No class found for the selected grade and division.', 'error')
                return redirect(url_for('add_student'))

            new_student = Students(
                first_name=first_name,
                last_name=last_name,
                id_num=id_num,
                guardian_id=guardian_id,
                class_id=class_row.id
            )
            db.session.add(new_student)
            db.session.commit()

            update_class_json(new_student, class_row)
            update_parent_json(new_student)

            flash('Student successfully added and JSON files updated.', 'success')
            return redirect(url_for('secretery_dashboard'))

        return render_template('add_student.html', form=form)
    else:
        return redirect(url_for('login'))

'''

#                              \\\\\\\
#                            \\\\\\\\\\\\
#                          \\\\\\\\\\\\\\\
#  -----------,-|           |C>   // )\\\\|
#           ,','|          /    || ,'/////|
#---------,','  |         (,    ||   /////
#        ||    |          \\  ||||//''''|
#        ||    |           |||||||     _|
#         ||    |______      `````\____/ \
#         ||    |     ,|         _/_____/ \
#        ||  ,'    ,' |        /          |
#        ||,'    ,'   |       |         \  |
#________|/    ,'     |      /           | |
#_____________,'      ,',_____|      |    | |
#            |     ,','      |      |    | |
#            |   ,','    ____|_____/    /  |
#            | ,','  __/ |             /   |
#____________|','   ///_/-------------/   |
#             |===========,'
#   ASHLEE IN THE FUTURE
# BEARD WILL BE LIKE THIS 
# I WISH




>>>>>>> backend/admin_func

if __name__ == "__main__":
    app = initialize_server()
    
    with app.app_context():
        DatabaseUtilityDAO.execute_sql_script("static/script.sql")
    
    app.run(debug=True)
