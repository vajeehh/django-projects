import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sms_project.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Staff, Student

print("Deleting all Staff/Students without a user account to clean up.")
Staff.objects.filter(user__isnull=True).delete()
Student.objects.filter(user__isnull=True).delete()
print("Cleanup done.")
