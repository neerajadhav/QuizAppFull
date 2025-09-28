from django.contrib import admin
from .models import QuizAttempt, QuizResponse, QuizAnalytics, QuestionAnalytics


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'quiz', 'status', 'score', 'start_time', 'end_time', 'time_taken']
    list_filter = ['status', 'quiz', 'start_time']
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'quiz__title']
    readonly_fields = ['start_time', 'score', 'total_questions', 'correct_answers', 'wrong_answers', 'unanswered', 'time_taken']
    ordering = ['-start_time']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student', 'quiz')


@admin.register(QuizResponse)
class QuizResponseAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'selected_option', 'is_correct', 'answered_at', 'time_taken']
    list_filter = ['is_correct', 'answered_at', 'attempt__quiz']
    search_fields = ['attempt__student__username', 'question__text']
    readonly_fields = ['answered_at', 'is_correct']
    ordering = ['-answered_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('attempt__student', 'question', 'selected_option')


@admin.register(QuizAnalytics)
class QuizAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'total_attempts', 'completed_attempts', 'average_score', 'highest_score', 'lowest_score', 'updated_at']
    readonly_fields = ['total_attempts', 'completed_attempts', 'average_score', 'highest_score', 'lowest_score', 'average_completion_time', 'created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('quiz')


@admin.register(QuestionAnalytics)
class QuestionAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['question', 'total_responses', 'correct_responses', 'accuracy_percentage', 'difficulty_level', 'updated_at']
    list_filter = ['difficulty_level', 'updated_at']
    readonly_fields = ['total_responses', 'correct_responses', 'wrong_responses', 'unanswered_count', 'difficulty_level', 'average_time_taken', 'created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def accuracy_percentage(self, obj):
        return f"{obj.accuracy_percentage:.1f}%"
    accuracy_percentage.short_description = 'Accuracy'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('question')
