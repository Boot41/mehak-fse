#!/usr/bin/env python
"""Test runner for job applications module."""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def setup_django():
    """Configure Django settings for testing."""
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'rest_framework',
            'rest_framework.authtoken',
            'job_applications',
        ],
        ROOT_URLCONF='job_applications.urls',
        REST_FRAMEWORK={
            'DEFAULT_AUTHENTICATION_CLASSES': [
                'rest_framework.authentication.TokenAuthentication',
            ],
            'TEST_REQUEST_DEFAULT_FORMAT': 'json',
            'TEST_REQUEST_RENDERER_CLASSES': [
                'rest_framework.renderers.JSONRenderer',
                'rest_framework.renderers.MultiPartRenderer',
            ],
        },
        MIDDLEWARE=[
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ],
        USE_OPENAI_FALLBACK=True,
        OPENAI_API_KEY='test-key',
        GOOGLE_CLIENT_SECRETS_FILE='test-credentials.json',
        GOOGLE_OAUTH_SCOPES=[
            'https://www.googleapis.com/auth/gmail.readonly'
        ],
        SECRET_KEY='test-key'
    )
    django.setup()
    
    # Create database tables
    call_command('migrate')

def run_tests():
    """Run all test cases."""
    # Setup Django
    setup_django()
    
    import unittest
    
    # Get all test files
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(
        start_dir=os.path.dirname(__file__),
        pattern='test_*.py'
    )
    
    # Run tests with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return 0 if all tests passed, 1 otherwise
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["job_applications.tests"])
    sys.exit(bool(failures))
