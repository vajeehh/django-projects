from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Students
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.student_create, name='student_create'),
    path('students/<int:pk>/edit/', views.student_update, name='student_update'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    
    # Staff
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/add/', views.staff_create, name='staff_create'),
    path('staff/<int:pk>/edit/', views.staff_update, name='staff_update'),
    path('staff/<int:pk>/delete/', views.staff_delete, name='staff_delete'),
    
    # Courses
    path('courses/', views.course_list, name='course_list'),
    path('courses/add/', views.course_create, name='course_create'),
    path('courses/<int:pk>/edit/', views.course_update, name='course_update'),
    path('courses/<int:pk>/delete/', views.course_delete, name='course_delete'),
    
    # Subjects
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/add/', views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/edit/', views.subject_update, name='subject_update'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),
    
    # Attendance
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/add/', views.attendance_create, name='attendance_create'),
    path('attendance/<int:pk>/edit/', views.attendance_update, name='attendance_update'),
    path('attendance/<int:pk>/delete/', views.attendance_delete, name='attendance_delete'),
    
    # Registration
    path('register/student/', views.student_register, name='student_register'),
    path('register/staff/', views.staff_register, name='staff_register'),
    
    # Approvals
    path('pending-approvals/', views.pending_approvals, name='pending_approvals'),
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
]
