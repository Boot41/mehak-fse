"""Tests for job application views.

This module contains tests for the job application API endpoints.
"""

from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from job_applications.models import Application
from job_applications.services.email_service import EmailService

User = get_user_model()


class ApplicationViewSetTests(TestCase):
    """Test cases for ApplicationViewSet."""

    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test application
        self.application = Application.objects.create(
            user=self.user,
            applicant_name='Test Applicant',
            job_title='Software Engineer',
            company_name='Test Company',
            email_content='test@company.com',
            status='applied'
        )
        
        # Setup API client
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        
        # Mock Gmail credentials
        self.test_credentials = {
            'token': 'test_token',
            'refresh_token': 'test_refresh_token',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret',
            'scopes': ['https://www.googleapis.com/auth/gmail.send']
        }
        
        # Add Gmail credentials to user
        self.user.gmail_credentials = self.test_credentials
        self.user.save()
        
        # URL for follow-up endpoint
        self.follow_up_url = reverse(
            'application-send-follow-up',
            kwargs={'pk': self.application.id}
        )

    @patch.object(EmailService, 'send_follow_up_email')
    def test_send_follow_up_success(self, mock_send_follow_up):
        """Test successful follow-up email sending."""
        # Mock successful email sending
        mock_send_follow_up.return_value = {
            'success': True,
            'message': 'Email sent successfully'
        }
        
        # Make request
        response = self.client.post(self.follow_up_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        mock_send_follow_up.assert_called_once_with(
            application_id=str(self.application.id),
            user_credentials=self.test_credentials
        )

    def test_send_follow_up_unauthenticated(self):
        """Test follow-up endpoint with unauthenticated user."""
        # Use unauthenticated client
        self.client.credentials()
        
        # Make request
        response = self.client.post(self.follow_up_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_send_follow_up_wrong_user(self):
        """Test follow-up endpoint with wrong user."""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # Use other user's client
        client = APIClient()
        refresh = RefreshToken.for_user(other_user)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        
        # Make request
        response = client.post(self.follow_up_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch.object(EmailService, 'send_follow_up_email')
    def test_send_follow_up_email_failure(self, mock_send_follow_up):
        """Test handling of email sending failure."""
        # Mock email sending failure
        mock_send_follow_up.return_value = {
            'success': False,
            'message': 'Failed to send email'
        }
        
        # Make request
        response = self.client.post(self.follow_up_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Failed to send email')

    def test_send_follow_up_invalid_application(self):
        """Test follow-up with invalid application ID."""
        # Create URL with invalid application ID
        url = reverse('application-send-follow-up', kwargs={'pk': 99999})
        
        # Make request
        response = self.client.post(url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Application not found')

    def test_send_follow_up_no_credentials(self):
        """Test follow-up without Gmail credentials."""
        # Remove Gmail credentials
        self.user.gmail_credentials = None
        self.user.save()
        
        # Make request
        response = self.client.post(self.follow_up_url)
        
        # Check response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Gmail credentials not found')
