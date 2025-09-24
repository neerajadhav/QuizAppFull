from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('quizzes/create/', views.create_quiz, name='create_quiz'),
    path('quizzes/<int:quiz_id>/', views.view_quiz, name='view_quiz'),
    path('quizzes/<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('quizzes/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('quizzes/<int:quiz_id>/add-questions/',
         views.add_questions, name='add_questions'),
    path('quizzes/question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
]
