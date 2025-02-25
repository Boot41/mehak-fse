"""Custom exceptions for Gmail API integration."""

class GmailAPIError(Exception):
    """Base exception for Gmail API errors."""
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class GmailRateLimitError(GmailAPIError):
    """Raised when Gmail API rate limit is exceeded."""
    def __init__(self, retry_after: int = None):
        self.retry_after = retry_after
        message = "Gmail API rate limit exceeded. Please try again later."
        super().__init__(message, status_code=429)

class GmailAuthError(GmailAPIError):
    """Raised when there are authentication issues with Gmail API."""
    def __init__(self, message: str = "Authentication failed. Please sign in again."):
        super().__init__(message, status_code=401)

class GmailNetworkError(GmailAPIError):
    """Raised when there are network connectivity issues."""
    def __init__(self, message: str = "Network error. Please check your connection."):
        super().__init__(message, status_code=503)

class GmailQuotaError(GmailAPIError):
    """Raised when Gmail API quota is exceeded."""
    def __init__(self):
        message = "Gmail API quota exceeded. Please try again later."
        super().__init__(message, status_code=429)
