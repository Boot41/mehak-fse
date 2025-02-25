"""Email service for job applications.

This module provides functionality for sending emails related to job applications.
"""

import logging
from django.conf import settings
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails using Gmail API."""

    def __init__(self):
        """Initialize the email service."""
        self.service = None

    def _get_gmail_service(self, credentials_dict):
        """Get Gmail API service instance."""
        try:
            credentials = Credentials(
                token=credentials_dict.get('token'),
                refresh_token=credentials_dict.get('refresh_token'),
                token_uri=credentials_dict.get('token_uri'),
                client_id=credentials_dict.get('client_id'),
                client_secret=credentials_dict.get('client_secret'),
                scopes=credentials_dict.get('scopes')
            )
            return build('gmail', 'v1', credentials=credentials)
        except Exception as e:
            logger.error(f"Error creating Gmail service: {str(e)}")
            raise

    def send_follow_up_email(self, application_id, user_credentials):
        """Send a follow-up email for a job application."""
        try:
            if not user_credentials:
                return {
                    'success': False,
                    'message': 'Gmail credentials not found'
                }

            service = self._get_gmail_service(user_credentials)
            
            # Create message
            message = MIMEText('This is a follow-up email for job application.')
            message['to'] = 'recipient@example.com'  # Replace with actual recipient
            message['subject'] = 'Follow-up: Job Application'
            
            # Encode the message
            raw = base64.urlsafe_b64encode(message.as_bytes())
            raw = raw.decode()
            
            # Send message
            service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()

            return {
                'success': True,
                'message': 'Follow-up email sent successfully'
            }
        except Exception as e:
            logger.error(f"Error sending follow-up email: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
