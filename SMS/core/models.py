from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    enroll_date = models.DateField(auto_now_add=True)
    courses = models.ManyToManyField(Course, blank=True, related_name='students')
    advisor = models.ForeignKey('Staff', on_delete=models.SET_NULL, null=True, blank=True, related_name='advised_students', limit_choices_to={'role': 'Teacher'}, verbose_name='Assigned Teacher/Advisor')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Staff(models.Model):
    ROLE_CHOICES = (
        ('Teacher', 'Teacher'),
        ('Admin', 'Admin'),
        ('Support', 'Support'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Teacher')
    hire_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subjects')
    teacher = models.ForeignKey('Staff', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_subjects', limit_choices_to={'role': 'Teacher'})

    def __str__(self):
        return f"{self.name} ({self.code})"

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='attendances', null=True)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Present')

    class Meta:
        unique_together = ('student', 'subject', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.date} ({self.status})"
