from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

def is_teacher(user):
    return getattr(user, 'role', '').lower() == 'teacher'

@user_passes_test(is_teacher)
def create_quiz(request):
    # Placeholder for quiz creation form
    return render(request, 'quizzes/create_quiz.html')
