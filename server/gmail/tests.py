"""Tests for Gmail integration."""

import base64
import json
import unittest
from unittest.mock import MagicMock, patch

from bs4 import BeautifulSoup
from googleapiclient.errors import HttpError

from .auth import GmailAuthService
from .email import GmailEmailService
from .parser import EmailParser


class TestGmailAuth(unittest.TestCase):
    """Test Gmail authentication functionality."""

    @patch('gmail.auth.Credentials')
    def test_get_credentials_from_file(self, mock_credentials):
        """Test loading credentials from file."""
        mock_credentials.from_authorized_user_file.return_value = MagicMock(valid=True)
        creds = GmailAuthService.get_credentials()
        self.assertIsNotNone(creds)

    @patch('gmail.auth.Credentials')
    def test_refresh_expired_credentials(self, mock_credentials):
        """Test refreshing expired credentials."""
        mock_creds = MagicMock(valid=False, expired=True, refresh_token=True)
        mock_credentials.from_authorized_user_file.return_value = mock_creds
        GmailAuthService.get_credentials()
        self.assertTrue(mock_creds.refresh.called)

    @patch('gmail.auth.InstalledAppFlow')
    def test_new_credentials_flow(self, mock_flow):
        """Test creating new credentials."""
        mock_flow.from_client_secrets_file.return_value = MagicMock()
        with patch('gmail.auth.Credentials') as mock_credentials:
            mock_credentials.from_authorized_user_file.side_effect = FileNotFoundError
            GmailAuthService.get_credentials()
            self.assertTrue(mock_flow.from_client_secrets_file.called)


class TestGmailEmail(unittest.TestCase):
    """Test email fetching and processing."""

    def setUp(self):
        """Set up test fixtures."""
        self.service_mock = MagicMock()
        self.auth_patcher = patch('gmail.email.GmailAuthService')
        self.mock_auth = self.auth_patcher.start()
        self.mock_auth.get_service.return_value = self.service_mock

    def tearDown(self):
        """Clean up test fixtures."""
        self.auth_patcher.stop()

    def test_fetch_emails_success(self):
        """Test successful email fetching."""
        # Mock message list response
        self.service_mock.users().messages().list().execute.return_value = {
            'messages': [{'id': '123'}, {'id': '456'}]
        }

        # Mock individual message responses
        def mock_get_message(userId, id, format):
            messages = {
                '123': {
                    'id': '123',
                    'threadId': 't1',
                    'labelIds': ['INBOX'],
                    'payload': {
                        'headers': [
                            {'name': 'Subject', 'value': 'Test Subject 1'},
                            {'name': 'From', 'value': 'test1@example.com'}
                        ],
                        'parts': [{
                            'mimeType': 'text/plain',
                            'body': {'data': base64.urlsafe_b64encode(b'Test body 1').decode()}
                        }]
                    }
                },
                '456': {
                    'id': '456',
                    'threadId': 't2',
                    'labelIds': ['INBOX'],
                    'payload': {
                        'headers': [
                            {'name': 'Subject', 'value': 'Test Subject 2'},
                            {'name': 'From', 'value': 'test2@example.com'}
                        ],
                        'parts': [{
                            'mimeType': 'text/plain',
                            'body': {'data': base64.urlsafe_b64encode(b'Test body 2').decode()}
                        }]
                    }
                }
            }
            return messages.get(id)

        self.service_mock.users().messages().get = MagicMock(
            side_effect=lambda userId, id, format: MagicMock(
                execute=lambda: mock_get_message(userId, id, format)
            )
        )

        emails = GmailEmailService.fetch_emails('test query', max_results=2)
        self.assertEqual(len(emails), 2)
        self.assertEqual(emails[0]['subject'], 'Test Subject 1')
        self.assertEqual(emails[1]['subject'], 'Test Subject 2')

    def test_fetch_emails_rate_limit(self):
        """Test handling of rate limit errors."""
        # Mock rate limit error
        error_response = MagicMock()
        error_response.status = 429
        self.service_mock.users().messages().list().execute.side_effect = [
            HttpError(error_response, b'Rate limit exceeded'),
            {'messages': []}  # Second call succeeds but returns no messages
        ]

        emails = GmailEmailService.fetch_emails('test query')
        self.assertEqual(len(emails), 0)  # Should handle error gracefully

    def test_fetch_emails_pagination(self):
        """Test email fetching with pagination."""
        # First page
        self.service_mock.users().messages().list().execute.side_effect = [
            {
                'messages': [{'id': '123'}],
                'nextPageToken': 'token1'
            },
            {
                'messages': [{'id': '456'}],
                'nextPageToken': None
            }
        ]

        # Mock get_message similar to previous test
        def mock_get_message(userId, id, format):
            return {
                'id': id,
                'threadId': f't{id}',
                'labelIds': ['INBOX'],
                'payload': {
                    'headers': [
                        {'name': 'Subject', 'value': f'Subject {id}'}
                    ],
                    'body': {'data': base64.urlsafe_b64encode(b'Test body').decode()}
                }
            }

        self.service_mock.users().messages().get = MagicMock(
            side_effect=lambda userId, id, format: MagicMock(
                execute=lambda: mock_get_message(userId, id, format)
            )
        )

        emails = GmailEmailService.fetch_emails('test query', max_results=2)
        self.assertEqual(len(emails), 2)
        self.assertEqual(emails[0]['id'], '123')
        self.assertEqual(emails[1]['id'], '456')


class TestEmailParser(unittest.TestCase):
    """Test email parsing functionality."""

    def test_parse_plain_text_email(self):
        """Test parsing plain text email."""
        email_data = {
            'body': """
            Dear John Smith,

            Thank you for applying for the position of Senior Developer at Acme Corp.
            """
        }
        result = EmailParser.parse_email(email_data)
        self.assertEqual(result['applicant_name'], 'John Smith')
        self.assertEqual(result['job_title'], 'Senior Developer')
        self.assertEqual(result['company_name'], 'Acme Corp')

    def test_parse_html_email(self):
        """Test parsing HTML email."""
        html = """
        <html>
            <body>
                <p>Dear Jane Doe,</p>
                <p>Thank you for applying for the Software Engineer position at Tech Inc.</p>
            </body>
        </html>
        """
        email_data = {'body': html}
        result = EmailParser.parse_email(email_data)
        self.assertEqual(result['applicant_name'], 'Jane Doe')
        self.assertEqual(result['job_title'], 'Software Engineer')
        self.assertEqual(result['company_name'], 'Tech Inc')

    def test_parse_missing_fields(self):
        """Test parsing email with missing fields."""
        email_data = {
            'body': "Thank you for your application."
        }
        result = EmailParser.parse_email(email_data)
        self.assertIsNone(result['applicant_name'])
        self.assertIsNone(result['job_title'])
        self.assertIsNone(result['company_name'])
        self.assertEqual(result['confidence_score'], 0)

    def test_parse_different_formats(self):
        """Test parsing different email formats."""
        formats = [
            (
                "Hi Alice Brown, We received your application for Data Scientist with XYZ Ltd.",
                {'applicant_name': 'Alice Brown', 'job_title': 'Data Scientist', 'company_name': 'XYZ Ltd'}
            ),
            (
                "Hello Bob Wilson! Thanks for applying to the Product Manager role at ABC Corp.",
                {'applicant_name': 'Bob Wilson', 'job_title': 'Product Manager', 'company_name': 'ABC Corp'}
            ),
            (
                "Dear Mr. Charlie Davis, Regarding your application for the DevOps Engineer position at Cloud Tech Inc.",
                {'applicant_name': 'Charlie Davis', 'job_title': 'DevOps Engineer', 'company_name': 'Cloud Tech Inc'}
            )
        ]

        for email_body, expected in formats:
            result = EmailParser.parse_email({'body': email_body})
            self.assertEqual(result['applicant_name'], expected['applicant_name'])
            self.assertEqual(result['job_title'], expected['job_title'])
            self.assertEqual(result['company_name'], expected['company_name'])


if __name__ == '__main__':
    unittest.main()
