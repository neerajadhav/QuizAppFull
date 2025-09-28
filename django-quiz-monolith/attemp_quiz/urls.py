from django.urls import path
from . import views

app_name = 'attemp_quiz'

urlpatterns = [
    # Student quiz attempt URLs
    path('', views.eligible_quizzes, name='eligible_quizzes'),
    path('start/<int:quiz_id>/', views.start_quiz, name='start_quiz'),
    path('take/<int:attempt_id>/', views.take_quiz, name='take_quiz'),
    path('submit-answer/<int:attempt_id>/', views.submit_answer, name='submit_answer'),
    path('submit/<int:attempt_id>/', views.submit_quiz, name='submit_quiz'),
    path('result/<int:attempt_id>/', views.quiz_result, name='quiz_result'),
    path('my-attempts/', views.my_attempts, name='my_attempts'),
    
    # Teacher analytics URLs
    path('analytics/<int:quiz_id>/', views.quiz_analytics_view, name='quiz_analytics'),
]
