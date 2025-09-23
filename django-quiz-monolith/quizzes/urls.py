from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('quizzes/create/', views.create_quiz, name='create_quiz'),
]