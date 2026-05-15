from django.contrib.auth.models import User

def pending_approvals_count(request):
    if request.user.is_authenticated and (hasattr(request.user, 'staff') or request.user.is_superuser):
        count = User.objects.filter(is_active=False).count()
        return {'pending_approvals_count': count}
    return {}
