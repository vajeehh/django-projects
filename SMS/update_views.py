import re

with open('core/views.py', 'r') as f:
    content = f.read()

# Add imports
imports = """from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

def staff_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'student') and not hasattr(request.user, 'staff') and not request.user.is_superuser:
            raise PermissionDenied("You must be staff to access this.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
"""
content = content.replace("from django.shortcuts import render, redirect, get_object_or_404\n", imports)

# Replace dashboard
dashboard_old = """def dashboard(request):
    # Calculate overall attendance percentage if we have records
    total_attendances = Attendance.objects.count()
    present_count = Attendance.objects.filter(status='Present').count()
    attendance_rate = 0
    if total_attendances > 0:
        attendance_rate = round((present_count / total_attendances) * 100)

    context = {
        'student_count': Student.objects.count(),
        'staff_count': Staff.objects.count(),
        'course_count': Course.objects.count(),
        'attendance_rate': attendance_rate,
        'recent_absences': Attendance.objects.filter(status='Absent').order_by('-date')[:5],
    }
    return render(request, 'core/dashboard.html', context)"""

dashboard_new = """@login_required
def dashboard(request):
    if hasattr(request.user, 'student') and not hasattr(request.user, 'staff') and not request.user.is_superuser:
        student = request.user.student
        total_attendances = Attendance.objects.filter(student=student).count()
        present_count = Attendance.objects.filter(student=student, status='Present').count()
        attendance_rate = round((present_count / total_attendances) * 100) if total_attendances > 0 else 0
        context = {
            'is_student': True,
            'attendance_rate': attendance_rate,
            'recent_absences': Attendance.objects.filter(student=student, status='Absent').order_by('-date')[:5],
        }
    else:
        total_attendances = Attendance.objects.count()
        present_count = Attendance.objects.filter(status='Present').count()
        attendance_rate = round((present_count / total_attendances) * 100) if total_attendances > 0 else 0
        context = {
            'student_count': Student.objects.count(),
            'staff_count': Staff.objects.count(),
            'course_count': Course.objects.count(),
            'attendance_rate': attendance_rate,
            'recent_absences': Attendance.objects.filter(status='Absent').order_by('-date')[:5],
        }
    return render(request, 'core/dashboard.html', context)"""

content = content.replace(dashboard_old, dashboard_new)

# Decorate specific views with staff_required
staff_views = ['student_list', 'student_create', 'student_update', 'student_delete', 
               'staff_list', 'staff_create', 'staff_update', 'staff_delete',
               'course_create', 'course_update', 'course_delete', 
               'attendance_create', 'attendance_update', 'attendance_delete']

for view in staff_views:
    content = re.sub(rf'^def {view}\(', f'@staff_required\ndef {view}(', content, flags=re.MULTILINE)

# Decorate other views with login_required
login_views = ['course_list']
for view in login_views:
    content = re.sub(rf'^def {view}\(', f'@login_required\ndef {view}(', content, flags=re.MULTILINE)

# For attendance_list, make it login_required, but filter based on role.
attendance_list_old = """def attendance_list(request):
    attendances = Attendance.objects.all().select_related('student', 'course').order_by('-date')
    return render(request, 'core/attendance_list.html', {'attendances': attendances})"""

attendance_list_new = """@login_required
def attendance_list(request):
    if hasattr(request.user, 'student') and not hasattr(request.user, 'staff') and not request.user.is_superuser:
        attendances = Attendance.objects.filter(student=request.user.student).select_related('student', 'course').order_by('-date')
    else:
        attendances = Attendance.objects.all().select_related('student', 'course').order_by('-date')
    return render(request, 'core/attendance_list.html', {'attendances': attendances})"""

content = content.replace(attendance_list_old, attendance_list_new)

with open('core/views.py', 'w') as f:
    f.write(content)
