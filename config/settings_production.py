"""
Production settings for QuizApp
"""

from .settings import *

# Production configuration
DEBUG = False
ALLOWED_HOSTS = ['*']  # Configure with your actual domain names

# Remove development-only apps and middleware
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'django_browser_reload']
MIDDLEWARE = [middleware for middleware in MIDDLEWARE 
              if middleware != 'django_browser_reload.middleware.BrowserReloadMiddleware']

# Add WhiteNoise for static file serving
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Static files configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_USE_FINDERS = True

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Optional: Environment variables for production
# SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)
# ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')
