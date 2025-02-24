"""Test package for job applications."""

from .test_views import ApplicationViewSetTests
from .test_email_service import EmailServiceTests

__all__ = [
    'ApplicationViewSetTests',
    'EmailServiceTests'
]
