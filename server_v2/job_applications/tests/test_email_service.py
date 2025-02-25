"""Tests for email service functionality.

This module contains tests for the email service used to send follow-up emails.
"""

from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone

from job_applications.models import Application
from job_applications.services.email_service import EmailService

User = get_user_model()


class EmailServiceTests(TestCase):
    """Test cases for EmailService."""

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
        
        # Mock Gmail credentials
        self.test_credentials = {
            'token': 'test_token',
            'refresh_token': 'test_refresh_token',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret',
            'scopes': ['https://www.googleapis.com/auth/gmail.send']
        }

    def test_generate_follow_up_content(self):
        """Test follow-up email content generation."""
        content = EmailService._generate_follow_up_content(self.application)
        
        # Check if content includes application details
        self.assertIn(self.application.job_title, content)
        self.assertIn(self.application.company_name, content)
        self.assertIn(self.application.applicant_name, content)
        self.assertIn(self.application.created_at.strftime('%B %d, %Y'), content)

    @patch('job_applications.services.email_service.build')
    def test_send_via_gmail_api_success(self, mock_build):
        """Test successful email sending via Gmail API."""
        # Mock Gmail API service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Mock message send
        mock_send = MagicMock()
        mock_service.users.return_value.messages.return_value.send = mock_send
        mock_send.return_value.execute.return_value = {'id': 'test_message_id'}
        
        # Send email
        result = EmailService._send_via_gmail_api(
            from_email='test@example.com',
            subject='Test Subject',
            body='Test Body',
            credentials=self.test_credentials
        )
        
        # Check result
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Email sent successfully via Gmail API')
        
        # Check if send was called correctly
        mock_send.assert_called_once()
        args = mock_send.call_args[1]
        self.assertEqual(args['userId'], 'me')
        self.assertIn('raw', args['body'])

    @patch('job_applications.services.email_service.build')
    def test_send_via_gmail_api_failure(self, mock_build):
        """Test Gmail API failure handling."""
        # Mock Gmail API service to raise exception
        mock_build.side_effect = Exception('Gmail API error')
        
        result = EmailService._send_via_gmail_api(
            from_email='test@example.com',
            subject='Test Subject',
            body='Test Body',
            credentials=self.test_credentials
        )
        
        self.assertFalse(result['success'])
        self.assertIn('Gmail API error', result['message'])

    @patch('job_applications.services.email_service.send_mail')
    def test_send_via_smtp_success(self, mock_send_mail):
        """Test successful email sending via SMTP."""
        mock_send_mail.return_value = 1
        
        result = EmailService._send_via_smtp(
            to_email='test@example.com',
            subject='Test Subject',
            body='Test Body'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Email sent successfully via SMTP')
        mock_send_mail.assert_called_once()

    @patch('job_applications.services.email_service.send_mail')
    def test_send_via_smtp_failure(self, mock_send_mail):
        """Test SMTP failure handling."""
        mock_send_mail.side_effect = Exception('SMTP error')
        
        result = EmailService._send_via_smtp(
            to_email='test@example.com',
            subject='Test Subject',
            body='Test Body'
        )
        
        self.assertFalse(result['success'])
        self.assertIn('SMTP error', result['message'])

    @patch.object(EmailService, '_send_via_gmail_api')
    def test_send_follow_up_email_success(self, mock_send_via_gmail):
        """Test successful follow-up email sending."""
        mock_send_via_gmail.return_value = {
            'success': True,
            'message': 'Email sent successfully via Gmail API'
        }
        
        result = EmailService.send_follow_up_email(
            application_id=self.application.id,
            user_credentials=self.test_credentials
        )
        
        self.assertTrue(result['success'])
        mock_send_via_gmail.assert_called_once()

    def test_send_follow_up_email_invalid_application(self):
        """Test handling of invalid application ID."""
        result = EmailService.send_follow_up_email(
            application_id=99999,
            user_credentials=self.test_credentials
        )
        
        self.assertFalse(result['success'])
        self.assertEqual(result['message'], 'Application not found')
