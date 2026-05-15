from core.forms import StudentForm, StaffForm
from django.contrib.auth.models import User
import sys

# Test Student Creation
student_data = {
    'username': 'teststudent',
    'password': 'password123',
    'first_name': 'Test',
    'last_name': 'Student',
    'email': 'teststudent@example.com',
    'courses': []
}
form = StudentForm(data=student_data)
if form.is_valid():
    student = form.save()
    if student.user and student.user.username == 'teststudent':
        print("SUCCESS: Student User created and linked.")
    else:
        print("ERROR: Student User not correctly linked.")
        sys.exit(1)
else:
    print("ERROR: Student Form invalid:", form.errors)
    sys.exit(1)

# Test Staff Creation
staff_data = {
    'username': 'teststaff',
    'password': 'password123',
    'first_name': 'Test',
    'last_name': 'Staff',
    'email': 'teststaff@example.com',
    'role': 'Admin'
}
form = StaffForm(data=staff_data)
if form.is_valid():
    staff = form.save()
    if staff.user and staff.user.username == 'teststaff':
        print("SUCCESS: Staff User created and linked.")
    else:
        print("ERROR: Staff User not correctly linked.")
        sys.exit(1)
else:
    print("ERROR: Staff Form invalid:", form.errors)
    sys.exit(1)

print("All form tests passed.")
