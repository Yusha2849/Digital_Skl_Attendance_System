import threading
import time
from datetime import datetime, timedelta

class Overseer:
    def __init__(self, json_manager, dao, report_generator,app, check_interval=25):
        """
        Overseer class to check for overdue registers and generate missing children reports.

        :param json_manager: Instance of JSONTimestampManager
        :param dao: Instance of your DAO (Data Access Object) to access the database
        :param report_generator: Instance of MissingChildrenReport for generating reports
        :param check_interval: How often to check the registers (default 45 minutes)
        """
        self.json_manager = json_manager
        self.dao = dao  # Using your DAO for database access
        self.report_generator = report_generator
        self.check_interval = check_interval
        self.overdue_report = None  # Store the latest compiled report
        self.app = app

    def start(self):
        """Start the overseer process in the background."""
        overseer_thread = threading.Thread(target=self.run)
        overseer_thread.daemon = True  # Daemon thread, won't block the main program
        overseer_thread.start()

    def run(self):
        """Run the overseer process that checks for overdue registers periodically."""
        while True:
            print("Overseer: Checking for overdue registers...")
            self.generate_report_for_overdue_classes()
            time.sleep(self.check_interval)

    # def check_overdue_registers(self):
    #     """Checks the JSON file for any overdue classes and triggers the report generation."""
    #     self.generate_report_for_overdue_classes()
        # data = self.json_manager.read_timestamps()
        # overdue_classes = []
        # current_time = datetime.now()

        # for class_id, timestamp_str in data.items():
        #     timestamp = datetime.fromisoformat(timestamp_str)
        #     if current_time - timestamp > timedelta(minutes=1):  # Overdue by 45 minutes
        #         overdue_classes.append(class_id)

        # if overdue_classes:
        #     print(f"Overdue classes: {overdue_classes}")
        #     self.overdue_report = self.generate_report_for_overdue_classes()
        # else:
        #     self.overdue_report = None

    def generate_report_for_overdue_classes(self):
        """Query the database (via DAO) and generate the missing students report."""
        # Query your DAO to get attendance records for overdue classes
        with self.app.app_context():
            attendance_records = self.dao.get_attendance_records_for_today()  
            
            formatted_data = self.format_attendence_records(attendance_records)
            # Use the MissingChildrenReport class to process the data
            self.report_generator.set_class_register_dict(formatted_data)  # Update attendance data
            missing_report = self.report_generator.get_missing_student_class_list()
            self.overdue_report = missing_report

    def format_attendence_records(self,data):
        formatted_data = {d.class_id:[[k,v[0],v[1]] for k, v in d.attendance_record_list.items()] for d in data}
        return formatted_data

    def get_overdue_report(self):
        """Return the latest compiled overdue report."""

        return self.overdue_report
