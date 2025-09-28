from django.apps import AppConfig


class AttempQuizConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attemp_quiz'
    verbose_name = 'Quiz Attempts'
    
    def ready(self):
        import attemp_quiz.signals
