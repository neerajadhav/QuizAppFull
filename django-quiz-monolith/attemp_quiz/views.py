from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.db import transaction
from quizzes.models import Quiz, Question, Option
from users.models import UserProfile
from .models import QuizAttempt, QuizResponse, QuizAnalytics, QuestionAnalytics
import json


@login_required
def eligible_quizzes(request):
    """Display quizzes that the student is eligible for"""
    if not request.user.is_student:
        messages.error(request, "Only students can access quizzes.")
        return redirect('frontend:home')
    
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        messages.error(request, "Please complete your profile to access quizzes.")
        return redirect('users:profile')
    
    # Get all quizzes that match student's degree and semester
    available_quizzes = Quiz.objects.filter(
        intent_degree=profile.degree,
        intent_semester=str(profile.current_semester)
    ).order_by('-created_at')
    
    # Check which quizzes the student has already attempted
    attempted_quiz_ids = QuizAttempt.objects.filter(
        student=request.user
    ).values_list('quiz_id', flat=True)
    
    context = {
        'available_quizzes': available_quizzes,
        'attempted_quiz_ids': attempted_quiz_ids,
        'student_profile': profile,
    }
    return render(request, 'attemp_quiz/eligible_quizzes.html', context)


@login_required
def start_quiz(request, quiz_id):
    """Start a new quiz attempt"""
    if not request.user.is_student:
        raise PermissionDenied("Only students can attempt quizzes.")
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        messages.error(request, "Please complete your profile to attempt quizzes.")
        return redirect('users:profile')
    
    # Check if student has already attempted this quiz
    existing_attempt = QuizAttempt.objects.filter(student=request.user, quiz=quiz).first()
    if existing_attempt:
        if existing_attempt.status == 'completed':
            messages.warning(request, "You have already completed this quiz.")
            return redirect('attemp_quiz:quiz_result', attempt_id=existing_attempt.id)
        else:
            # Continue existing attempt
            return redirect('attemp_quiz:take_quiz', attempt_id=existing_attempt.id)
    
    # Create new attempt
    with transaction.atomic():
        attempt = QuizAttempt.objects.create(
            student=request.user,
            quiz=quiz,
            status='started'
        )
        
        # Validate eligibility
        if not attempt.is_student_eligible():
            attempt.delete()
            messages.error(request, "You are not eligible for this quiz based on your degree and semester.")
            return redirect('attemp_quiz:eligible_quizzes')
        
        # Create analytics record if it doesn't exist
        analytics, created = QuizAnalytics.objects.get_or_create(quiz=quiz)
        if created:
            analytics.update_analytics()
    
    messages.success(request, f"Quiz '{quiz.title}' started successfully!")
    return redirect('attemp_quiz:take_quiz', attempt_id=attempt.id)


@login_required
def take_quiz(request, attempt_id):
    """Display quiz questions for student to answer"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    
    if attempt.status == 'completed':
        return redirect('attemp_quiz:quiz_result', attempt_id=attempt.id)
    
    # Update status to in_progress if it's still started
    if attempt.status == 'started':
        attempt.status = 'in_progress'
        attempt.save()
    
    questions = attempt.quiz.questions.all().order_by('id')
    
    # Get existing responses
    responses = {
        resp.question_id: resp for resp in 
        QuizResponse.objects.filter(attempt=attempt).select_related('selected_option')
    }
    
    context = {
        'attempt': attempt,
        'questions': questions,
        'responses': responses,
    }
    return render(request, 'attemp_quiz/take_quiz.html', context)


@login_required
@require_http_methods(["POST"])
def submit_answer(request, attempt_id):
    """Handle individual question answer submission via AJAX"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    
    if attempt.status == 'completed':
        return JsonResponse({'error': 'Quiz already completed'}, status=400)
    
    try:
        data = json.loads(request.body)
        question_id = data.get('question_id')
        option_id = data.get('option_id')
        time_taken_seconds = data.get('time_taken', 0)
        
        question = get_object_or_404(Question, id=question_id, quiz=attempt.quiz)
        option = get_object_or_404(Option, id=option_id, question=question) if option_id else None
        
        # Create or update response
        response, created = QuizResponse.objects.get_or_create(
            attempt=attempt,
            question=question,
            defaults={
                'selected_option': option,
                'time_taken': timezone.timedelta(seconds=time_taken_seconds)
            }
        )
        
        if not created:
            response.selected_option = option
            response.time_taken = timezone.timedelta(seconds=time_taken_seconds)
            response.save()
        
        # Update question analytics
        question_analytics, created = QuestionAnalytics.objects.get_or_create(question=question)
        question_analytics.update_analytics()
        
        return JsonResponse({
            'success': True,
            'is_correct': response.is_correct,
            'correct_option_id': question.options.filter(is_correct=True).first().id if question.options.filter(is_correct=True).exists() else None
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def submit_quiz(request, attempt_id):
    """Submit the entire quiz and calculate final score"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    
    if attempt.status == 'completed':
        messages.warning(request, "Quiz already completed.")
        return redirect('attemp_quiz:quiz_result', attempt_id=attempt.id)
    
    with transaction.atomic():
        attempt.complete_attempt()
        
        # Update quiz analytics
        analytics, created = QuizAnalytics.objects.get_or_create(quiz=attempt.quiz)
        analytics.update_analytics()
    
    messages.success(request, f"Quiz submitted successfully! Your score: {attempt.score:.1f}%")
    return redirect('attemp_quiz:quiz_result', attempt_id=attempt.id)


@login_required
def quiz_result(request, attempt_id):
    """Display quiz results"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    
    if attempt.status != 'completed':
        messages.warning(request, "Please complete the quiz first.")
        return redirect('attemp_quiz:take_quiz', attempt_id=attempt.id)
    
    responses = QuizResponse.objects.filter(attempt=attempt).select_related(
        'question', 'selected_option'
    ).order_by('question__id')
    
    context = {
        'attempt': attempt,
        'responses': responses,
    }
    return render(request, 'attemp_quiz/quiz_result.html', context)


@login_required
def my_attempts(request):
    """Display all quiz attempts by the current student"""
    if not request.user.is_student:
        raise PermissionDenied("Only students can view their attempts.")
    
    attempts = QuizAttempt.objects.filter(
        student=request.user
    ).select_related('quiz').order_by('-start_time')
    
    context = {
        'attempts': attempts,
    }
    return render(request, 'attemp_quiz/my_attempts.html', context)


@login_required
def quiz_analytics_view(request, quiz_id):
    """Display detailed analytics for a quiz (for teachers)"""
    if not request.user.is_teacher:
        raise PermissionDenied("Only teachers can view quiz analytics.")
    
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    
    # Get or create analytics
    analytics, created = QuizAnalytics.objects.get_or_create(quiz=quiz)
    if created or not analytics.updated_at or (timezone.now() - analytics.updated_at).days > 0:
        analytics.update_analytics()
    
    # Get detailed attempts data
    attempts = QuizAttempt.objects.filter(quiz=quiz).select_related(
        'student', 'student__profile'
    ).order_by('-start_time')
    
    # Get question-wise analytics
    question_analytics = []
    for question in quiz.questions.all():
        q_analytics, created = QuestionAnalytics.objects.get_or_create(question=question)
        if created or not q_analytics.updated_at or (timezone.now() - q_analytics.updated_at).hours > 1:
            q_analytics.update_analytics()
        question_analytics.append({
            'question': question,
            'analytics': q_analytics
        })
    
    # Calculate additional metrics
    completion_rate = (analytics.completed_attempts / analytics.total_attempts * 100) if analytics.total_attempts > 0 else 0
    
    # Grade distribution
    completed_attempts = attempts.filter(status='completed')
    grade_distribution = {
        'A': completed_attempts.filter(score__gte=90).count(),
        'B': completed_attempts.filter(score__gte=80, score__lt=90).count(),
        'C': completed_attempts.filter(score__gte=70, score__lt=80).count(),
        'D': completed_attempts.filter(score__gte=60, score__lt=70).count(),
        'F': completed_attempts.filter(score__lt=60).count(),
    }
    
    context = {
        'quiz': quiz,
        'analytics': analytics,
        'attempts': attempts,
        'question_analytics': question_analytics,
        'completion_rate': completion_rate,
        'grade_distribution': grade_distribution,
    }
    return render(request, 'attemp_quiz/quiz_analytics.html', context)
