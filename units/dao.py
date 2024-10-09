from datetime import date
from .models import Admin, Secretary, Educator, Guardian, Student, SchoolClass, AttendanceRecord, db
from sqlalchemy import text
from flask import current_app
from werkzeug.security import check_password_hash

class UserDAO:
    @staticmethod
    def get_user_by_username(username):
        # Try to find the user in the Admin, Secretary, Educator, or Guardian tables
        if username.startswith('a'):
            user = Admin.query.filter_by(username=username).first()
        elif username.startswith('s'):
            user = Secretary.query.filter_by(username=username).first()
        elif username.startswith('e'):
            user = Educator.query.filter_by(username=username).first()
        elif username.startswith('p'):
            user = Guardian.query.filter_by(username=username).first()
        else:
            user = None
        return user

    @staticmethod
    def check_password(user, password):
        # Check password based on the user type
        if isinstance(user, Admin):
            return check_password_hash(user.password, password)
        elif isinstance(user, Secretary):
            return check_password_hash(user.password, password)
        elif isinstance(user, Educator):
            return check_password_hash(user.password, password)
        elif isinstance(user, Guardian):
            return check_password_hash(user.password, password)
        return False

class AdminDAO:
    @staticmethod
    def get_all_admins():
        return Admin.query.all()

    @staticmethod
    def get_admin_by_id(admin_id):
        return Admin.query.get(admin_id)

    @staticmethod
    def add_admin(username, password, email):
        new_admin = Admin(username=username, password=password, email=email)
        db.session.add(new_admin)
        db.session.commit()
        print("Admin added:", new_admin)  # Debug output

    @staticmethod
    def delete_admin(admin_id):
        admin = Admin.query.get(admin_id)
        if admin:
            db.session.delete(admin)
            db.session.commit()

class SecretaryDAO:
    @staticmethod
    def get_all_secretaries():
        return Secretary.query.all()

    @staticmethod
    def get_secretary_by_id(secretary_id):
        return Secretary.query.get(secretary_id)

    @staticmethod
    def add_secretary(username, password, first_name, last_name, email, cell_number, rsa_id_num):
        new_secretary = Secretary(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            cell_number=cell_number,
            rsa_id_num=rsa_id_num
        )
        db.session.add(new_secretary)
        db.session.commit()

    @staticmethod
    def check_unique_fields(email, cell_number, rsa_id_num):
        existing_secretary = Secretary.query.filter(
            (Secretary.email == email) | 
            (Secretary.cell_number == cell_number) | 
            (Secretary.rsa_id_num == rsa_id_num)
        ).first()

        return existing_secretary is not None 

    @staticmethod
    def delete_secretary(secretary_id):
        secretary = Secretary.query.get(secretary_id)
        if secretary:
            db.session.delete(secretary)
            db.session.commit()

class EducatorDAO:
    @staticmethod
    def get_all_educators():
        return Educator.query.all()

    @staticmethod
    def get_educator_by_id(educator_id):
        return Educator.query.get(educator_id)

    @staticmethod
    def add_educator(username, password, first_name, last_name, email, cell_number, rsa_id_num):
        new_educator = Educator(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            cell_number=cell_number,
            rsa_id_num=rsa_id_num
        )
        db.session.add(new_educator)
        db.session.commit()

    @staticmethod
    def check_unique_fields(email, cell_number, rsa_id_num):
        existing_secretary = Educator.query.filter(
            (Educator.email == email) | 
            (Educator.cell_number == cell_number) | 
            (Educator.rsa_id_num == rsa_id_num)
        ).first()

        return existing_secretary is not None 

    @staticmethod
    def delete_educator(educator_id):
        educator = Educator.query.get(educator_id)
        if educator:
            db.session.delete(educator)
            db.session.commit()

class GuardianDAO:
    @staticmethod
    def get_all_guardians():
        return Guardian.query.all()

    @staticmethod
    def get_guardian_by_id(guardian_id):
        return Guardian.query.get(guardian_id)

    @staticmethod
    def add_guardian(username, password, first_name, last_name, email, cell_number, address, rsa_id_number):
        
        guardian_dependants_list = []
        
        new_guardian = Guardian(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            cell_number=cell_number,
            address=address,
            rsa_id_number=rsa_id_number,
            guardian_dependants_list=guardian_dependants_list  
        )
        db.session.add(new_guardian)
        db.session.commit()

    @staticmethod
    def check_unique_fields(email, cell_number, rsa_id_number):
        existing_secretary = Guardian.query.filter(
            (Guardian.email == email) | 
            (Guardian.cell_number == cell_number) | 
            (Guardian.rsa_id_number == rsa_id_number)
        ).first()

        return existing_secretary is not None 

    @staticmethod
    def delete_guardian(guardian_id):
        guardian = Guardian.query.get(guardian_id)
        if guardian:
            db.session.delete(guardian)
            db.session.commit()

class StudentDAO:
    @staticmethod
    def get_all_students():
        return Student.query.all()

    @staticmethod
    def get_student_by_id(student_id):
        return Student.query.get(student_id)

    @staticmethod
    def add_student(first_name, last_name, rsa_id_number, guardian_id):
        new_student = Student(
            first_name=first_name,
            last_name=last_name,
            rsa_id_number=rsa_id_number,
            guardian_id=guardian_id
        )
        db.session.add(new_student)
        db.session.commit()

        return new_student
    
    @staticmethod
    def check_unique_fields(rsa_id_number):
        existing_secretary = Student.query.filter(
            (Student.rsa_id_number == rsa_id_number)
        ).first()

        return existing_secretary is not None 

    @staticmethod
    def delete_student(student_id):
        student = Student.query.get(student_id)
        if student:
            db.session.delete(student)
            db.session.commit()

class SchoolClassDAO:

    @staticmethod
    def get_all_classrooms():      
        return SchoolClass.query.all()
    
    @staticmethod
    def get_all_classes():
        classroom = SchoolClass.query.all()
        return [(cls.class_id, f"Grade {cls.grade} - {cls.division}") for cls in classroom]

    @staticmethod
    def get_class_by_id(class_id):
        return SchoolClass.query.get(class_id)

    @staticmethod
    def add_class(educator_id,grade, division, class_students):
        new_class = SchoolClass(
            educator_id=educator_id,
            grade=grade,
            division=division,
            class_students=class_students
        )
        db.session.add(new_class)
        db.session.commit()

    @staticmethod
    def delete_class(class_id):
        class_ = SchoolClass.query.get(class_id)
        if class_:
            db.session.delete(class_)
            db.session.commit()

    @staticmethod
    def check_unique_class(grade, division):
        """
        Check if a class with the same grade and division already exists.
        Returns True if a duplicate class exists, otherwise False.
        """
        existing_class = SchoolClass.query.filter_by(grade=grade, division=division).first()
        return existing_class is not None

    @staticmethod
    def check_educator_allocation(educator_id):
        """
        Check if the educator is already allocated to a class.
        Returns True if the educator is already allocated, otherwise False.
        """
        allocated_class = SchoolClass.query.filter_by(educator_id=educator_id).first()
        return allocated_class is not None

class AttendanceRecordDAO:
    @staticmethod
    def get_all_attendance_records():
        return AttendanceRecord.query.all()

    @staticmethod
    def get_attendance_record_by_id(attendance_record_id):
        return AttendanceRecord.query.get(attendance_record_id)
    
    @staticmethod
    def get_attendance_records_for_today():
        # Get today's date
        today = date.today()

        # Query to get attendance records where the attendance_record_date matches today's date
        return AttendanceRecord.query.filter_by(attendance_record_date=today).all()

        
    @staticmethod
    def add_attendance_record(attendance_record_date, attendance_record_list, class_id):
        new_record = AttendanceRecord(
            attendance_record_date=attendance_record_date,
            attendance_record_list=attendance_record_list,
            class_id=class_id
        )
        db.session.add(new_record)
        db.session.commit()

    @staticmethod
    def delete_attendance_record(attendance_record_id):
        record = AttendanceRecord.query.get(attendance_record_id)
        if record:
            db.session.delete(record)
            db.session.commit()
    

# Utility class for handling database script execution
class DatabaseUtilityDAO:
    @staticmethod
    def execute_sql_script(script_path):
        """Executes the given SQL script using Flask-SQLAlchemy's db engine."""
        try:
            # Open the SQL script file
            with open(script_path, 'r') as file:
                sql_script = file.read()

            # Log the database path for debugging
            print(f"Executing SQL script for database at: {current_app.config['SQLALCHEMY_DATABASE_URI']}")

            # Execute the script in the Flask app context
            with current_app.app_context():
                with db.engine.begin() as connection:  # 'begin()' ensures auto-commit
                    for statement in sql_script.split(';'):
                        if statement.strip():  # Avoid executing empty statements
                            try:
                                connection.execute(text(statement))
                            except Exception as stmt_error:
                                print(f"Error executing statement: {statement.strip()}\nError: {stmt_error}")
        except Exception as e:
            print(f"Error executing script: {e}")
