from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from wagtail.models import Page
from home.models import HomePage
from .models import Quiz, Question, AnswerOption, QuizAttempt, StudentAnswer


class MultipleChoiceSelectionTest(TestCase):
	def setUp(self):
		self.client = Client()
		self.user = User.objects.create_user(username='student', password='pass12345')
		# Minimal quiz page required fields
		# Get or create root home page
		self.home_page = HomePage.objects.first()
		if not self.home_page:
			root = Page.get_first_root_node()
			self.home_page = HomePage(title='Home', slug='home')
			root.add_child(instance=self.home_page)
			self.home_page.save_revision().publish()

		self.quiz = Quiz(
			title='Test Quiz',
			slug='test-quiz',
			created_by=self.user,
			duration_minutes=10,
			show_results_immediately=True,
			is_active=True,
		)
		self.home_page.add_child(instance=self.quiz)
		self.quiz.save_revision().publish()

		# Multiple choice question with 3 correct answers
		self.question = Question.objects.create(
			quiz=self.quiz,
			question_text='Select all prime numbers',
			question_type='multiple',
			marks=3,
			is_required=True,
		)
		# Add options
		self.opt2 = AnswerOption.objects.create(question=self.question, option_text='2', is_correct=True)
		self.opt3 = AnswerOption.objects.create(question=self.question, option_text='3', is_correct=True)
		self.opt5 = AnswerOption.objects.create(question=self.question, option_text='5', is_correct=True)
		self.opt4 = AnswerOption.objects.create(question=self.question, option_text='4', is_correct=False)

	def test_all_multiple_choice_options_saved(self):
		self.client.login(username='student', password='pass12345')
		start_url = reverse('start_quiz', args=[self.quiz.id])
		resp = self.client.get(start_url)
		self.assertEqual(resp.status_code, 302)
		attempt = QuizAttempt.objects.filter(student=self.user, quiz=self.quiz).latest('start_time')
		take_url = reverse('take_quiz', args=[attempt.id])

		# Post with new [] naming convention
		post_data = {
			f'question_{self.question.id}[]': [str(self.opt2.id), str(self.opt3.id), str(self.opt5.id)]
		}
		resp = self.client.post(take_url, post_data, follow=True)
		self.assertEqual(resp.status_code, 200)
		attempt.refresh_from_db()
		answer = StudentAnswer.objects.get(attempt=attempt, question=self.question)
		selected_ids = set(answer.selected_options.values_list('id', flat=True))
		self.assertEqual(selected_ids, {self.opt2.id, self.opt3.id, self.opt5.id})
		self.assertTrue(answer.is_correct)

	def test_legacy_name_still_supported(self):
		self.client.login(username='student', password='pass12345')
		start_url = reverse('start_quiz', args=[self.quiz.id])
		self.client.get(start_url)
		attempt = QuizAttempt.objects.filter(student=self.user, quiz=self.quiz).latest('start_time')
		take_url = reverse('take_quiz', args=[attempt.id])

		# Post with legacy naming (without [])
		post_data = {
			f'question_{self.question.id}': [str(self.opt2.id), str(self.opt3.id), str(self.opt5.id)]
		}
		resp = self.client.post(take_url, post_data, follow=True)
		self.assertEqual(resp.status_code, 200)
		answer = StudentAnswer.objects.get(attempt=attempt, question=self.question)
		selected_ids = set(answer.selected_options.values_list('id', flat=True))
		self.assertEqual(selected_ids, {self.opt2.id, self.opt3.id, self.opt5.id})
		self.assertTrue(answer.is_correct)
