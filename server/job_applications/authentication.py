"""Custom authentication for job applications API."""

from rest_framework import authentication
from rest_framework import exceptions


class CustomAuthentication(authentication.BaseAuthentication):
    """Custom authentication that returns 401 instead of 403 for unauthenticated requests."""

    def authenticate(self, request):
        """Authenticate the request."""
        user = getattr(request._request, 'user', None)
        if not user or not user.is_authenticated:
            raise exceptions.AuthenticationFailed('Authentication credentials were not provided.')
        return (user, None)
