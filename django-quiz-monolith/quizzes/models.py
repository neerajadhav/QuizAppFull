
from django.db import models
from users.models import User

DEGREE_CHOICES = [
	('btech', 'BTech (4 years)'),
	('mtech', 'MTech (2 years)'),
]

SEMESTER_CHOICES = {
	'btech': [(str(i), f'Semester {i}') for i in range(1, 9)],
	'mtech': [(str(i), f'Semester {i}') for i in range(1, 5)],
}

class Quiz(models.Model):
	title = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)

	intent_degree = models.CharField(max_length=10, choices=DEGREE_CHOICES, blank=True, null=True)
	ALL_SEMESTER_CHOICES = SEMESTER_CHOICES['btech'] + SEMESTER_CHOICES['mtech']
	intent_semester = models.CharField(max_length=2, choices=ALL_SEMESTER_CHOICES, blank=True, null=True)

class Question(models.Model):
	quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
	text = models.TextField()
	image = models.ImageField(upload_to='question_images/', blank=True, null=True)

class Option(models.Model):
	question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
	text = models.CharField(max_length=255)
	image = models.ImageField(upload_to='option_images/', blank=True, null=True)
	is_correct = models.BooleanField(default=False)
