import os
import django
from django.test import Client
from django.contrib.auth.models import User

# Setup django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sms_project.settings')
django.setup()

client = Client()

print("Testing Student Registration...")
response = client.post('/register/student/', {
    'username': 'newstudent1',
    'password': 'password123',
    'first_name': 'New',
    'last_name': 'Student',
    'email': 'newstudent@example.com',
    'courses': []
})

# Should return 200 with the success template
if response.status_code == 200 and b'Registration Submitted' in response.content:
    print("SUCCESS: Registration view returned success page.")
else:
    print(f"FAILED: Registration view returned status {response.status_code}")
    exit(1)

# Verify user created but inactive
user = User.objects.get(username='newstudent1')
if not user.is_active:
    print("SUCCESS: User created and is inactive.")
else:
    print("FAILED: User is active.")
    exit(1)

print("All tests passed.")
