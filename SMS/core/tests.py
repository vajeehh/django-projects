from django.test import TestCase
from .models import Course, Student, Staff

class ModelTests(TestCase):
    def test_course_creation(self):
        course = Course.objects.create(name='Mathematics', code='MATH101', description='Basic Math')
        self.assertEqual(course.name, 'Mathematics')
        self.assertEqual(str(course), 'Mathematics (MATH101)')

    def test_student_creation(self):
        student = Student.objects.create(first_name='John', last_name='Doe', email='john@example.com')
        self.assertEqual(student.first_name, 'John')
        self.assertEqual(str(student), 'John Doe')

    def test_staff_creation(self):
        staff = Staff.objects.create(first_name='Jane', last_name='Smith', email='jane@example.com', role='Admin')
        self.assertEqual(staff.role, 'Admin')
        self.assertEqual(str(staff), 'Jane Smith (Admin)')
