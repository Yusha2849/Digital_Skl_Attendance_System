# from prettytable import attendance_record

class MissingStudentIdentifier:
    def __init__(self, data_structure):
        """
        Initializes the system with a data structure and sets up an empty list 
        for tracking missing students.
        
        :param data_structure: A list of lists containing student information.
        Each entry follows the structure: [STUDENT_ID, LEAVE_BIT, PRESENT_BIT]
        """
        # This holds the student data as a list of lists
        self.data_structure = data_structure
        # This list will hold references to all missing students in a class
        self.missing_student_list = []  

    def identify_missing_students(self):
        """
        Identifies and prints the status of each student (Present, Absent, or Missing).
        If a student is "Missing", they are added to the missing_student_list.
        """
        for record in self.data_structure:
            student_id = record[0]
            leave_bit = record[1]
            present_bit = record[2]

            # Get the student status based on leave_bit and present_bit
            status = self.get_student_status(leave_bit, present_bit)
            # print(f"{student_id} is {status}")

            # If student is missing, add to the missing student list
            if self.identify_missing_student(status):
                self.add_missing_student(student_id)

    def get_student_status(self, leave_bit, present_bit):
        """
        Determines the student's status based on the LEAVE_BIT and PRESENT_BIT.
        
        LEAVE_BIT -> Whether the student should be in school today.
        PRESENT_BIT -> Whether the student was present when the register was marked.
        
        Returns:
            - "Absent" if LEAVE_BIT == 1 and PRESENT_BIT == 0.
            - "Present" if LEAVE_BIT == 0 and PRESENT_BIT == 1.
            - "Missing" if both LEAVE_BIT and PRESENT_BIT == 0.
        """
        if leave_bit == 1 and present_bit == 0:
            return "Absent"
        if leave_bit == 0 and present_bit == 1:
            return "Present"
        if leave_bit == 0 and present_bit == 0:
            return "Missing"
        else:
            return None

    def add_missing_student(self, student_id):
        """
        Adds a student to the missing_student_list if they are not already present.
        
        :param student_id: The ID of the student to add.
        """
        if student_id not in self.missing_student_list:  # Check if student is already added
            self.missing_student_list.append(student_id)

    def remove_missing_student(self, student_id):
        """
        Removes a student from the missing_student_list if they are present.
        
        :param student_id: The ID of the student to remove.
        """
        if student_id in self.missing_student_list:  # Check if student exists before removing
            self.missing_student_list.remove(student_id)

    def get_missing_students(self):
        """Returns the list of missing students."""
        
        #Validation if missing student list is empty
        if not self.missing_student_list:
            self.identify_missing_students()
            
        
        return self.missing_student_list

    # Lambda function to identify if a student is missing
    identify_missing_student = lambda self, student_status: student_status == "Missing"