"""Custom error handlers for the job applications API.

This module provides custom exception handling for the API, ensuring consistent
error responses across all endpoints.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from .exceptions import (
    ApplicationValidationError,
    DuplicateApplicationError,
    ApplicationNotFoundError
)


def custom_exception_handler(exc, context):
    """Handle exceptions and return appropriate responses.
    
    Args:
        exc: The exception that was raised
        context: The context in which the exception was raised
        
    Returns:
        Response object with appropriate status code and error message
    """
    # First try the default handler
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the default response
        if isinstance(exc, ApplicationValidationError):
            response.status_code = status.HTTP_400_BAD_REQUEST
            response.data = {
                'error': 'Validation Error',
                'detail': exc.detail
            }
        elif isinstance(exc, DuplicateApplicationError):
            response.status_code = status.HTTP_409_CONFLICT
            response.data = {
                'error': 'Duplicate Application',
                'detail': exc.detail or 'An application for this job already exists'
            }
        elif isinstance(exc, ApplicationNotFoundError):
            response.status_code = status.HTTP_404_NOT_FOUND
            response.data = {
                'error': 'Not Found',
                'detail': exc.detail or 'Application not found or access denied'
            }
        else:
            # For other DRF exceptions
            response.data = {
                'error': str(exc.__class__.__name__),
                'detail': response.data
            }
        return response

    # Handle Django exceptions
    if isinstance(exc, DjangoValidationError):
        return Response(
            {
                'error': 'Validation Error',
                'detail': exc.message_dict if hasattr(exc, 'message_dict') else str(exc)
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    elif isinstance(exc, IntegrityError):
        return Response(
            {
                'error': 'Database Error',
                'detail': 'A database error occurred. Please try again.'
            },
            status=status.HTTP_409_CONFLICT
        )
    elif isinstance(exc, PermissionError):
        return Response(
            {
                'error': 'Permission Denied',
                'detail': 'You do not have permission to perform this action'
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # For unhandled exceptions, return a generic error
    return Response(
        {
            'error': 'Internal Server Error',
            'detail': 'An unexpected error occurred. Please try again later.'
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
