from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import QuizAttempt, QuizResponse, QuizAnalytics, QuestionAnalytics


@receiver(post_save, sender=QuizAttempt)
def update_quiz_analytics_on_attempt_change(sender, instance, created, **kwargs):
    """Update quiz analytics when a quiz attempt is created or updated"""
    analytics, created = QuizAnalytics.objects.get_or_create(quiz=instance.quiz)
    analytics.update_analytics()


@receiver(post_delete, sender=QuizAttempt)
def update_quiz_analytics_on_attempt_delete(sender, instance, **kwargs):
    """Update quiz analytics when a quiz attempt is deleted"""
    try:
        analytics = QuizAnalytics.objects.get(quiz=instance.quiz)
        analytics.update_analytics()
    except QuizAnalytics.DoesNotExist:
        pass


@receiver(post_save, sender=QuizResponse)
def update_question_analytics_on_response_change(sender, instance, created, **kwargs):
    """Update question analytics when a response is created or updated"""
    analytics, created = QuestionAnalytics.objects.get_or_create(question=instance.question)
    analytics.update_analytics()


@receiver(post_delete, sender=QuizResponse)
def update_question_analytics_on_response_delete(sender, instance, **kwargs):
    """Update question analytics when a response is deleted"""
    try:
        analytics = QuestionAnalytics.objects.get(question=instance.question)
        analytics.update_analytics()
    except QuestionAnalytics.DoesNotExist:
        pass
