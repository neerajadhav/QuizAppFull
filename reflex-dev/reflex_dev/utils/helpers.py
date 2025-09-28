"""Helper utility functions."""

import re
import secrets
import string
from datetime import datetime


def format_date(date_str: str) -> str:
    """Format date string for display."""
    try:
        date_obj = datetime.fromisoformat(date_str)
        return date_obj.strftime("%B %d, %Y")
    except (ValueError, TypeError):
        return date_str


def validate_email(email: str) -> bool:
    """Validate email format."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None


def generate_id(prefix: str = "", length: int = 8) -> str:
    """Generate a random ID with optional prefix."""
    characters = string.ascii_uppercase + string.digits
    random_part = ''.join(secrets.choice(characters) for _ in range(length))
    
    if prefix:
        return f"{prefix}{random_part}"
    return random_part


def validate_student_id(student_id: str) -> bool:
    """Validate student ID format (you can customize this)."""
    # Example: STU + 6 digits
    pattern = r'^STU\d{6}$'
    return re.match(pattern, student_id) is not None


def validate_teacher_id(teacher_id: str) -> bool:
    """Validate teacher ID format (you can customize this)."""
    # Example: TCH + 6 digits
    pattern = r'^TCH\d{6}$'
    return re.match(pattern, teacher_id) is not None


def sanitize_input(input_str: str) -> str:
    """Sanitize user input by removing potentially harmful characters."""
    if not input_str:
        return ""
    
    # Remove HTML tags and script tags
    input_str = re.sub(r'<[^>]+>', '', input_str)
    
    # Remove potentially harmful characters
    input_str = re.sub(r'[<>"\';()&+]', '', input_str)
    
    return input_str.strip()
