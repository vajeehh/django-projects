from django.contrib import admin
from .models import Course, Student, Staff, Attendance, Subject

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'enroll_date')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('enroll_date', 'courses')

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'role', 'hire_date')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('role', 'hire_date')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'course', 'teacher')
    list_filter = ('course', 'teacher')
    search_fields = ('name', 'code')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'date', 'status')
    list_filter = ('date', 'status', 'subject')
    search_fields = ('student__first_name', 'student__last_name', 'subject__name')
