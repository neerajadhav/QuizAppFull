from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from users.models import User, UserProfile
from quizzes.models import Quiz, Question, Option


class QuizAttempt(models.Model):
    """Model to track quiz attempts by students"""
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='started')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    wrong_answers = models.PositiveIntegerField(default=0)
    unanswered = models.PositiveIntegerField(default=0)
    time_taken = models.DurationField(null=True, blank=True)  # Total time taken to complete
    
    class Meta:
        unique_together = ['student', 'quiz']
        ordering = ['-start_time']
    
    def clean(self):
        super().clean()
        # Check if student meets eligibility criteria
        if self.student and self.quiz:
            if not self.is_student_eligible():
                raise ValidationError("Student is not eligible for this quiz based on degree and semester requirements.")
    
    def is_student_eligible(self):
        """Check if student is eligible for this quiz based on degree and semester"""
        if not self.student.is_student:
            return False
            
        try:
            profile = self.student.profile
        except UserProfile.DoesNotExist:
            return False
        
        # Check degree eligibility
        if self.quiz.intent_degree and profile.degree:
            if profile.degree != self.quiz.intent_degree:
                return False
        
        # Check semester eligibility
        if self.quiz.intent_semester and profile.current_semester:
            if str(profile.current_semester) != self.quiz.intent_semester:
                return False
        
        return True
    
    def calculate_score(self):
        """Calculate the score based on correct answers"""
        if self.total_questions == 0:
            return 0
        return (self.correct_answers / self.total_questions) * 100
    
    def update_score(self):
        """Update score and answer counts based on responses"""
        responses = self.responses.all()
        self.total_questions = responses.count()
        self.correct_answers = responses.filter(is_correct=True).count()
        self.wrong_answers = responses.filter(is_correct=False, selected_option__isnull=False).count()
        self.unanswered = responses.filter(selected_option__isnull=True).count()
        self.score = self.calculate_score()
        
        if self.status == 'completed' and self.start_time and self.end_time:
            self.time_taken = self.end_time - self.start_time
        
        self.save()
    
    def complete_attempt(self):
        """Mark attempt as completed and calculate final score"""
        self.status = 'completed'
        self.end_time = timezone.now()
        self.update_score()
    
    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} ({self.status})"


class QuizResponse(models.Model):
    """Model to store individual question responses"""
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE, null=True, blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)
    time_taken = models.DurationField(null=True, blank=True)  # Time taken to answer this question
    
    class Meta:
        unique_together = ['attempt', 'question']
        ordering = ['answered_at']
    
    def save(self, *args, **kwargs):
        # Automatically determine if the answer is correct
        if self.selected_option:
            self.is_correct = self.selected_option.is_correct
        else:
            self.is_correct = False
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.attempt.student.username} - Q{self.question.id} - {'Correct' if self.is_correct else 'Wrong'}"


class QuizAnalytics(models.Model):
    """Model to store analytics data for quizzes"""
    quiz = models.OneToOneField(Quiz, on_delete=models.CASCADE, related_name='analytics')
    total_attempts = models.PositiveIntegerField(default=0)
    completed_attempts = models.PositiveIntegerField(default=0)
    average_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    highest_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    lowest_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    average_completion_time = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def update_analytics(self):
        """Update analytics based on quiz attempts"""
        attempts = QuizAttempt.objects.filter(quiz=self.quiz)
        completed_attempts = attempts.filter(status='completed')
        
        self.total_attempts = attempts.count()
        self.completed_attempts = completed_attempts.count()
        
        if completed_attempts.exists():
            scores = completed_attempts.values_list('score', flat=True)
            self.average_score = sum(scores) / len(scores)
            self.highest_score = max(scores)
            self.lowest_score = min(scores)
            
            # Calculate average completion time
            completion_times = completed_attempts.exclude(time_taken__isnull=True).values_list('time_taken', flat=True)
            if completion_times:
                total_seconds = sum(ct.total_seconds() for ct in completion_times)
                avg_seconds = total_seconds / len(completion_times)
                self.average_completion_time = timezone.timedelta(seconds=avg_seconds)
        
        self.save()
    
    def __str__(self):
        return f"Analytics for {self.quiz.title}"


class QuestionAnalytics(models.Model):
    """Model to store analytics for individual questions"""
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='analytics')
    total_responses = models.PositiveIntegerField(default=0)
    correct_responses = models.PositiveIntegerField(default=0)
    wrong_responses = models.PositiveIntegerField(default=0)
    unanswered_count = models.PositiveIntegerField(default=0)
    difficulty_level = models.CharField(max_length=20, default='medium')  # easy, medium, hard
    average_time_taken = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def accuracy_percentage(self):
        """Calculate accuracy percentage for this question"""
        if self.total_responses == 0:
            return 0
        return (self.correct_responses / self.total_responses) * 100
    
    def update_analytics(self):
        """Update analytics based on responses to this question"""
        responses = QuizResponse.objects.filter(question=self.question)
        
        self.total_responses = responses.count()
        self.correct_responses = responses.filter(is_correct=True).count()
        self.wrong_responses = responses.filter(is_correct=False, selected_option__isnull=False).count()
        self.unanswered_count = responses.filter(selected_option__isnull=True).count()
        
        # Calculate difficulty level based on accuracy
        accuracy = self.accuracy_percentage
        if accuracy >= 80:
            self.difficulty_level = 'easy'
        elif accuracy >= 50:
            self.difficulty_level = 'medium'
        else:
            self.difficulty_level = 'hard'
        
        # Calculate average time taken
        timed_responses = responses.exclude(time_taken__isnull=True).values_list('time_taken', flat=True)
        if timed_responses:
            total_seconds = sum(tt.total_seconds() for tt in timed_responses)
            avg_seconds = total_seconds / len(timed_responses)
            self.average_time_taken = timezone.timedelta(seconds=avg_seconds)
        
        self.save()
    
    def __str__(self):
        return f"Analytics for Question {self.question.id} ({self.difficulty_level})"
