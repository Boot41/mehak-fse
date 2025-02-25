"""Custom exceptions for job applications."""

from rest_framework.exceptions import APIException
from rest_framework import status


class ApplicationValidationError(APIException):
    """Exception raised when application data validation fails."""
    
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid application data'
    default_code = 'invalid_application'


class DuplicateApplicationError(APIException):
    """Exception raised when a duplicate application is detected."""
    
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Application already exists'
    default_code = 'duplicate_application'


class ApplicationNotFoundError(APIException):
    """Exception raised when an application is not found."""
    
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Application not found'
    default_code = 'application_not_found'
