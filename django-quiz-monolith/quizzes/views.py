from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test

def is_teacher(user):
    return getattr(user, 'role', '').lower() == 'teacher'

@user_passes_test(is_teacher)
def create_quiz(request):
    if request.method == 'POST':
        quiz_title = request.POST.get('quiz_title', '').strip()
        quiz_description = request.POST.get('quiz_description', '').strip()
        if quiz_title:
            from .models import Quiz
            quiz = Quiz.objects.create(
                title=quiz_title,
                description=quiz_description,
                created_by=request.user
            )
            return redirect('quizzes:view_quiz', quiz_id=quiz.id)
        else:
            error = "Quiz title is required."
            return render(request, 'quizzes/create_quiz.html', {'error': error, 'quiz_title': quiz_title, 'quiz_description': quiz_description})
    return render(request, 'quizzes/create_quiz.html')


@user_passes_test(is_teacher)
def delete_question(request, question_id):
    from .models import Question
    question = get_object_or_404(Question, id=question_id)
    quiz_id = question.quiz.id
    if request.method == 'POST':
        question.delete()
        return redirect('quizzes:view_quiz', quiz_id=quiz_id)
    # for safety, do not allow GET deletes
    return render(request, 'quizzes/confirm_delete.html', {'question': question})

@user_passes_test(is_teacher)
def view_quiz(request, quiz_id):
    from .models import Quiz, Question, Option
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    success = False
    errors = []

    if request.method == 'POST':
        question_id = request.POST.get('question_id')
        q_text = request.POST.get('question_text', '').strip()
        q_image = request.FILES.get('question_image')
        correct_option = request.POST.get('correct_option', '')

        if q_text:
            options = []
            for opt in ['a', 'b', 'c', 'd']:
                opt_text = request.POST.get(f'option_{opt}', '').strip()
                opt_image = request.FILES.get(f'option_{opt}_image')
                is_correct = correct_option == opt
                if opt_text:
                    options.append((opt_text, opt_image, is_correct))

            if len(options) < 3:
                errors.append("At least 3 options are required.")
            else:
                if question_id:  # Editing existing question
                    try:
                        question = Question.objects.get(id=question_id, quiz=quiz)
                        question.text = q_text
                        if q_image:
                            question.image = q_image
                        question.save()

                        # Delete existing options and create new ones
                        question.options.all().delete()
                        for opt_text, opt_image, is_correct in options:
                            Option.objects.create(
                                question=question,
                                text=opt_text,
                                image=opt_image,
                                is_correct=is_correct
                            )
                        success = True
                    except Question.DoesNotExist:
                        errors.append("Question not found.")
                else:  # Creating new question
                    question = Question.objects.create(
                        quiz=quiz,
                        text=q_text,
                        image=q_image
                    )
                    for opt_text, opt_image, is_correct in options:
                        Option.objects.create(
                            question=question,
                            text=opt_text,
                            image=opt_image,
                            is_correct=is_correct
                        )
                    success = True

            if success:
                return redirect('quizzes:view_quiz', quiz_id=quiz.id)
        else:
            errors.append("Question text is required.")

    return render(request, 'quizzes/view_quiz.html', {'quiz': quiz, 'success': success, 'errors': errors})

@user_passes_test(is_teacher)
def edit_quiz(request, quiz_id):
    from .models import Quiz
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    
    if request.method == 'POST':
        quiz_title = request.POST.get('quiz_title', '').strip()
        quiz_description = request.POST.get('quiz_description', '').strip()
        if quiz_title:
            quiz.title = quiz_title
            quiz.description = quiz_description
            quiz.save()
            return redirect('quizzes:view_quiz', quiz_id=quiz.id)
        else:
            error = "Quiz title is required."
            return render(request, 'quizzes/edit_quiz.html', {'quiz': quiz, 'error': error})
    
    return render(request, 'quizzes/edit_quiz.html', {'quiz': quiz})

@user_passes_test(is_teacher)
def delete_quiz(request, quiz_id):
    from .models import Quiz
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    
    if request.method == 'POST':
        quiz.delete()
        return redirect('users:dashboard')
    
    return render(request, 'quizzes/confirm_delete_quiz.html', {'quiz': quiz})
