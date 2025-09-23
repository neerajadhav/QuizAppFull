# Quiz App - Django Monolith

A Django web application for creating and managing quizzes.

## Setup

This project uses Python virtual environment and Django 5.2.6.

### Prerequisites

- Python 3.13+
- pip

### Installation

1. Clone the repository
2. Navigate to the project directory:
   ```bash
   cd django-quiz-monolith
   ```

3. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. Run database migrations:
   ```bash
   python manage.py migrate
   ```

2. Start the development server:
   ```bash
   python manage.py runserver
   ```

3. Open your browser and visit `http://127.0.0.1:8000/`

### Development

- The virtual environment is located in `.venv/`
- Main Django project settings are in `quiz_app/`
- Use `python manage.py` commands for Django operations

### Project Structure

```
django-quiz-monolith/
├── .venv/                 # Virtual environment
├── quiz_app/              # Main Django project
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```
