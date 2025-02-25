"""Test package for job applications."""

from .test_views import JobApplicationViewSetTests
from .test_integration import JobApplicationIntegrationTests

__all__ = [
    'JobApplicationViewSetTests',
    'JobApplicationIntegrationTests'
]
