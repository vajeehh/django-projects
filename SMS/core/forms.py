from django import forms
from django.contrib.auth.models import User
from .models import Student, Staff, Course, Subject, Attendance
from datetime import date

class StudentForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['username'].required = False
            self.fields['password'].required = False

    class Meta:
        model = Student
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'courses', 'advisor']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'courses': forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-list'}),
            'advisor': forms.Select(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        student = super().save(commit=False)
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if commit:
            if username and password and not student.user_id:
                user = User.objects.create_user(username=username, email=student.email, password=password, first_name=student.first_name, last_name=student.last_name)
                student.user = user
            student.save()
            self.save_m2m()
        return student

class StaffForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['username'].required = False
            self.fields['password'].required = False

    class Meta:
        model = Staff
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'role']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        staff = super().save(commit=False)
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if commit:
            if username and password and not staff.user_id:
                user = User.objects.create_user(username=username, email=staff.email, password=password, first_name=staff.first_name, last_name=staff.last_name)
                staff.user = user
            staff.save()
        return staff

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'code', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'course', 'teacher']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
        }

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'subject', 'date', 'status']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['max'] = date.today().strftime('%Y-%m-%d')
        
        if self.user and hasattr(self.user, 'staff') and self.user.staff.role == 'Teacher' and not self.user.is_superuser:
            teacher = self.user.staff
            self.fields['subject'].queryset = Subject.objects.filter(teacher=teacher)
            self.fields['student'].queryset = Student.objects.filter(courses__subjects__teacher=teacher).distinct()

    def clean_date(self):
        entered_date = self.cleaned_data.get('date')
        if entered_date and entered_date > date.today():
            raise forms.ValidationError("Attendance cannot be recorded for a future date.")
        return entered_date

class StudentRegistrationForm(StudentForm):
    def save(self, commit=True):
        student = super().save(commit=False)
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if commit:
            if username and password and not student.user_id:
                user = User.objects.create_user(username=username, email=student.email, password=password, first_name=student.first_name, last_name=student.last_name)
                user.is_active = False 
                user.save()
                student.user = user
            student.save()
            self.save_m2m()
        return student

class StaffRegistrationForm(StaffForm):
    def save(self, commit=True):
        staff = super().save(commit=False)
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if commit:
            if username and password and not staff.user_id:
                user = User.objects.create_user(username=username, email=staff.email, password=password, first_name=staff.first_name, last_name=staff.last_name)
                user.is_active = False 
                user.save()
                staff.user = user
            staff.save()
        return staff
