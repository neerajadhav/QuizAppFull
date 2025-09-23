from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    """Home page view"""
    return render(request, 'frontend/home.html')

@login_required
def dashboard(request):
    """Dashboard view that redirects based on user role"""
    if request.user.is_student:
        return render(request, 'users/student_dashboard.html')
    elif request.user.is_teacher:
        return render(request, 'users/teacher_dashboard.html')
    else:
        return render(request, 'frontend/dashboard.html')
