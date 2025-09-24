from django.contrib import admin
from .models import Quiz, Question, Option

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at', 'question_count')
    list_filter = ('created_at', 'created_by')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)

    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Questions'

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'option_count')
    list_filter = ('quiz',)
    search_fields = ('text', 'quiz__title')
    readonly_fields = ('id',)

    def option_count(self, obj):
        return obj.options.count()
    option_count.short_description = 'Options'

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    list_filter = ('is_correct', 'question__quiz')
    search_fields = ('text', 'question__text', 'question__quiz__title')
    readonly_fields = ('id',)
