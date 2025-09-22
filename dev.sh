#!/bin/bash

# QuizApp Development Script
# This script helps manage the Django application with Tailwind CSS

PYTHON_PATH="/home/super/Documents/QuizAppFull/.venv/bin/python"
PROJECT_DIR="/home/super/Documents/QuizAppFull"

cd "$PROJECT_DIR"

case "$1" in
    "runserver")
        echo "Starting Django development server..."
        $PYTHON_PATH manage.py runserver
        ;;
    "tailwind")
        echo "Starting Tailwind CSS watch mode..."
        $PYTHON_PATH manage.py tailwind start
        ;;
    "build")
        echo "Building Tailwind CSS for production..."
        $PYTHON_PATH manage.py tailwind build
        ;;
    "migrate")
        echo "Running database migrations..."
        $PYTHON_PATH manage.py migrate
        ;;
    "makemigrations")
        echo "Creating new migrations..."
        $PYTHON_PATH manage.py makemigrations
        ;;
    "collectstatic")
        echo "Collecting static files..."
        $PYTHON_PATH manage.py collectstatic --noinput
        ;;
    "createsuperuser")
        echo "Creating superuser..."
        $PYTHON_PATH manage.py createsuperuser
        ;;
    "shell")
        echo "Starting Django shell..."
        $PYTHON_PATH manage.py shell
        ;;
    "test")
        echo "Running tests..."
        $PYTHON_PATH manage.py test
        ;;
    "dev")
        echo "Starting development environment..."
        echo "This will start both Django server and Tailwind watch mode..."
        echo "Open two terminals and run:"
        echo "1. ./dev.sh runserver"
        echo "2. ./dev.sh tailwind"
        ;;
    *)
        echo "QuizApp Development Helper"
        echo "Usage: ./dev.sh [command]"
        echo ""
        echo "Available commands:"
        echo "  runserver       - Start Django development server"
        echo "  tailwind        - Start Tailwind CSS watch mode"
        echo "  build          - Build Tailwind CSS for production"
        echo "  migrate        - Run database migrations"
        echo "  makemigrations - Create new migrations"
        echo "  collectstatic  - Collect static files"
        echo "  createsuperuser - Create admin user"
        echo "  shell          - Start Django shell"
        echo "  test           - Run tests"
        echo "  dev            - Show development setup instructions"
        ;;
esac
