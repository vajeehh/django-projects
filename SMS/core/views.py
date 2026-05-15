from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q

def staff_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'student') and not hasattr(request.user, 'staff') and not request.user.is_superuser:
            raise PermissionDenied("You must be staff to access this.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied("You must be an administrator to access this.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
    
from .models import Student, Staff, Course, Subject, Attendance
from .forms import StudentForm, StaffForm, CourseForm, SubjectForm, AttendanceForm, StudentRegistrationForm, StaffRegistrationForm
from django.contrib.auth.models import User
from django.contrib import messages

import json
from datetime import date, timedelta

@login_required
def dashboard(request):
    last_7_days = [date.today() - timedelta(days=i) for i in range(6, -1, -1)]
    seven_days_dates_json = json.dumps([d.strftime('%b %d') for d in last_7_days])

    if hasattr(request.user, 'student') and not hasattr(request.user, 'staff') and not request.user.is_superuser:
        student = request.user.student
        total_attendances = Attendance.objects.filter(student=student).count()
        present_count = Attendance.objects.filter(student=student, status='Present').count()
        attendance_rate = round((present_count / total_attendances) * 100) if total_attendances > 0 else 0
        
        present_trend = []
        absent_trend = []
        for d in last_7_days:
            present_trend.append(Attendance.objects.filter(student=student, date=d, status='Present').count())
            absent_trend.append(Attendance.objects.filter(student=student, date=d, status='Absent').count())
            
        subject_names = []
        subject_rates = []
        for course in student.courses.all():
            for subject in course.subjects.all():
                total = Attendance.objects.filter(student=student, subject=subject).count()
                pres = Attendance.objects.filter(student=student, subject=subject, status='Present').count()
                if total > 0:
                    subject_names.append(subject.name)
                    subject_rates.append(round((pres/total)*100))

        context = {
            'is_student': True,
            'attendance_rate': attendance_rate,
            'recent_absences': Attendance.objects.filter(student=student, status='Absent').order_by('-date')[:5],
            'seven_days_dates_json': seven_days_dates_json,
            'present_trend_json': json.dumps(present_trend),
            'absent_trend_json': json.dumps(absent_trend),
            'subject_names_json': json.dumps(subject_names),
            'subject_rates_json': json.dumps(subject_rates),
        }
    elif hasattr(request.user, 'staff') and request.user.staff.role == 'Teacher' and not request.user.is_superuser:
        teacher = request.user.staff
        students_count = Student.objects.filter(Q(advisor=teacher) | Q(courses__subjects__teacher=teacher)).distinct().count()
        subjects_count = Subject.objects.filter(teacher=teacher).count()
        
        total_attendances = Attendance.objects.filter(subject__teacher=teacher).count()
        present_count = Attendance.objects.filter(subject__teacher=teacher, status='Present').count()
        attendance_rate = round((present_count / total_attendances) * 100) if total_attendances > 0 else 0

        present_trend = []
        absent_trend = []
        for d in last_7_days:
            present_trend.append(Attendance.objects.filter(subject__teacher=teacher, date=d, status='Present').count())
            absent_trend.append(Attendance.objects.filter(subject__teacher=teacher, date=d, status='Absent').count())
            
        subject_names = []
        subject_rates = []
        for subject in Subject.objects.filter(teacher=teacher):
            total = Attendance.objects.filter(subject=subject).count()
            pres = Attendance.objects.filter(subject=subject, status='Present').count()
            if total > 0:
                subject_names.append(subject.name)
                subject_rates.append(round((pres/total)*100))
        
        context = {
            'is_teacher': True,
            'student_count': students_count,
            'subject_count': subjects_count,
            'attendance_rate': attendance_rate,
            'recent_absences': Attendance.objects.filter(subject__teacher=teacher, status='Absent').order_by('-date')[:5],
            'seven_days_dates_json': seven_days_dates_json,
            'present_trend_json': json.dumps(present_trend),
            'absent_trend_json': json.dumps(absent_trend),
            'subject_names_json': json.dumps(subject_names),
            'subject_rates_json': json.dumps(subject_rates),
        }
    else:
        total_attendances = Attendance.objects.count()
        present_count = Attendance.objects.filter(status='Present').count()
        attendance_rate = round((present_count / total_attendances) * 100) if total_attendances > 0 else 0

        present_trend = []
        absent_trend = []
        for d in last_7_days:
            present_trend.append(Attendance.objects.filter(date=d, status='Present').count())
            absent_trend.append(Attendance.objects.filter(date=d, status='Absent').count())
            
        subject_names = []
        subject_rates = []
        for subject in Subject.objects.all():
            total = Attendance.objects.filter(subject=subject).count()
            pres = Attendance.objects.filter(subject=subject, status='Present').count()
            if total > 0:
                subject_names.append(subject.name)
                subject_rates.append(round((pres/total)*100))
                
        course_names = []
        course_student_counts = []
        for course in Course.objects.all():
            if course.students.count() > 0:
                course_names.append(course.name)
                course_student_counts.append(course.students.count())

        context = {
            'student_count': Student.objects.count(),
            'staff_count': Staff.objects.count(),
            'course_count': Course.objects.count(),
            'attendance_rate': attendance_rate,
            'recent_absences': Attendance.objects.filter(status='Absent').order_by('-date')[:5],
            'seven_days_dates_json': seven_days_dates_json,
            'present_trend_json': json.dumps(present_trend),
            'absent_trend_json': json.dumps(absent_trend),
            'subject_names_json': json.dumps(subject_names),
            'subject_rates_json': json.dumps(subject_rates),
            'course_names_json': json.dumps(course_names),
            'course_student_counts_json': json.dumps(course_student_counts),
        }
    return render(request, 'core/dashboard.html', context)

# --- Students ---

@staff_required
def student_list(request):
    if hasattr(request.user, 'staff') and request.user.staff.role == 'Teacher' and not request.user.is_superuser:
        teacher = request.user.staff
        students = Student.objects.filter(Q(advisor=teacher) | Q(courses__subjects__teacher=teacher)).distinct().order_by('-enroll_date')
    else:
        students = Student.objects.all().order_by('-enroll_date')
    return render(request, 'core/student_list.html', {'students': students})

@admin_required
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student added successfully!')
            return redirect('core:student_list')
    else:
        form = StudentForm()
    return render(request, 'core/student_form.html', {'form': form, 'title': 'Add Student'})

@admin_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully!')
            return redirect('core:student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'core/student_form.html', {'form': form, 'title': 'Edit Student'})

@admin_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully!')
        return redirect('core:student_list')
    return render(request, 'core/confirm_delete.html', {'object': student, 'title': 'Delete Student'})

# --- Staff ---

@admin_required
def staff_list(request):
    staff_members = Staff.objects.all().order_by('-hire_date')
    return render(request, 'core/staff_list.html', {'staff_members': staff_members})

@admin_required
def staff_create(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff member added successfully!')
            return redirect('core:staff_list')
    else:
        form = StaffForm()
    return render(request, 'core/staff_form.html', {'form': form, 'title': 'Add Staff'})

@admin_required
def staff_update(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff updated successfully!')
            return redirect('core:staff_list')
    else:
        form = StaffForm(instance=staff)
    return render(request, 'core/staff_form.html', {'form': form, 'title': 'Edit Staff'})

@admin_required
def staff_delete(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        staff.delete()
        messages.success(request, 'Staff deleted successfully!')
        return redirect('core:staff_list')
    return render(request, 'core/confirm_delete.html', {'object': staff, 'title': 'Delete Staff'})

# --- Courses ---

@login_required
def course_list(request):
    if hasattr(request.user, 'student') and not hasattr(request.user, 'staff') and not request.user.is_superuser:
        courses = request.user.student.courses.all().order_by('name')
    elif hasattr(request.user, 'staff') and request.user.staff.role == 'Teacher' and not request.user.is_superuser:
        courses = Course.objects.filter(subjects__teacher=request.user.staff).distinct().order_by('name')
    else:
        courses = Course.objects.all().order_by('name')
    return render(request, 'core/course_list.html', {'courses': courses})

@admin_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course added successfully!')
            return redirect('core:course_list')
    else:
        form = CourseForm()
    return render(request, 'core/course_form.html', {'form': form, 'title': 'Add Course'})

@admin_required
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('core:course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'core/course_form.html', {'form': form, 'title': 'Edit Course'})

@admin_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        return redirect('core:course_list')
    return render(request, 'core/confirm_delete.html', {'object': course, 'title': 'Delete Course'})

# --- Subjects ---

@login_required
def subject_list(request):
    if hasattr(request.user, 'student') and not hasattr(request.user, 'staff') and not request.user.is_superuser:
        subjects = Subject.objects.filter(course__in=request.user.student.courses.all()).order_by('course__name', 'name')
    elif hasattr(request.user, 'staff') and request.user.staff.role == 'Teacher' and not request.user.is_superuser:
        subjects = Subject.objects.filter(teacher=request.user.staff).order_by('course__name', 'name')
    else:
        subjects = Subject.objects.all().order_by('course__name', 'name')
    return render(request, 'core/subject_list.html', {'subjects': subjects})

@admin_required
def subject_create(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject added successfully!')
            return redirect('core:subject_list')
    else:
        form = SubjectForm()
    return render(request, 'core/subject_form.html', {'form': form, 'title': 'Add Subject'})

@admin_required
def subject_update(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated successfully!')
            return redirect('core:subject_list')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'core/subject_form.html', {'form': form, 'title': 'Edit Subject'})

@admin_required
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Subject deleted successfully!')
        return redirect('core:subject_list')
    return render(request, 'core/confirm_delete.html', {'object': subject, 'title': 'Delete Subject'})

# --- Attendance ---

@login_required
def attendance_list(request):
    if hasattr(request.user, 'student') and not hasattr(request.user, 'staff') and not request.user.is_superuser:
        attendances = Attendance.objects.filter(student=request.user.student).select_related('student', 'subject').order_by('-date')
    else:
        attendances = Attendance.objects.all().select_related('student', 'subject').order_by('-date')
    return render(request, 'core/attendance_list.html', {'attendances': attendances})

@staff_required
def attendance_create(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Attendance record added successfully!')
            return redirect('core:attendance_list')
    else:
        form = AttendanceForm(user=request.user)
    return render(request, 'core/attendance_form.html', {'form': form, 'title': 'Record Attendance'})

@staff_required
def attendance_update(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Attendance record updated successfully!')
            return redirect('core:attendance_list')
    else:
        form = AttendanceForm(instance=attendance, user=request.user)
    return render(request, 'core/attendance_form.html', {'form': form, 'title': 'Edit Attendance'})

@staff_required
def attendance_delete(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    if request.method == 'POST':
        attendance.delete()
        messages.success(request, 'Attendance record deleted successfully!')
        return redirect('core:attendance_list')
    return render(request, 'core/confirm_delete.html', {'object': attendance, 'title': 'Delete Attendance Record'})

# --- Registration and Approvals ---

def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'registration/register_success.html', {'role': 'Student'})
    else:
        form = StudentRegistrationForm()
    return render(request, 'registration/register_student.html', {'form': form, 'title': 'Student Registration'})

def staff_register(request):
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'registration/register_success.html', {'role': 'Staff'})
    else:
        form = StaffRegistrationForm()
    return render(request, 'registration/register_staff.html', {'form': form, 'title': 'Staff Registration'})

@admin_required
def pending_approvals(request):
    users = User.objects.filter(is_active=False).select_related('student', 'staff')
    return render(request, 'core/pending_approvals.html', {'users': users})

@admin_required
def approve_user(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, pk=user_id)
        user.is_active = True
        user.save()
        messages.success(request, f'User {user.username} has been approved.')
    return redirect('core:pending_approvals')
