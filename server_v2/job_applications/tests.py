"""Tests for job applications."""

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from unittest.mock import patch, MagicMock

from .models import JobApplication


class JobApplicationModelTest(TestCase):
    """Test cases for JobApplication model."""

    def setUp(self):
        """Set up test data."""
        self.application = JobApplication.objects.create(
            applicant_name="John Smith",
            job_title="Software Engineer",
            company_name="TechCorp",
            job_id="REQ-12345",
            email_body="Test email body",
            date_received=timezone.now(),
            confidence_score=100,
            email_subject="Job Application",
            email_sender="john@example.com"
        )

    def test_string_representation(self):
        """Test the string representation of the model."""
        self.assertEqual(
            str(self.application),
            "John Smith - Software Engineer at TechCorp"
        )

    def test_ordering(self):
        """Test that applications are ordered by date_received."""
        JobApplication.objects.create(
            applicant_name="Jane Doe",
            job_title="Data Scientist",
            company_name="DataCorp",
            email_body="Another test email",
            date_received=timezone.now() + timezone.timedelta(days=1),
            email_sender="jane@example.com"
        )
        applications = JobApplication.objects.all()
        self.assertEqual(applications[0].applicant_name, "Jane Doe")
        self.assertEqual(applications[1].applicant_name, "John Smith")


class JobApplicationViewTest(TestCase):
    """Test cases for JobApplicationView."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.url = reverse('job_applications:job_applications')
        self.sample_email = {
            'applicant_name': 'John Smith',
            'job_title': 'Software Engineer',
            'company_name': 'TechCorp',
            'job_id': 'REQ-12345',
            'body': 'Test email body',
            'date': timezone.now(),
            'confidence_score': 100,
            'subject': 'Job Application',
            'sender': 'john@example.com'
        }

    def test_get_applications(self):
        """Test getting list of applications."""
        # Create some test applications
        JobApplication.objects.create(
            applicant_name="John Smith",
            job_title="Software Engineer",
            company_name="TechCorp",
            email_body="Test email body",
            email_sender="john@example.com"
        )
        JobApplication.objects.create(
            applicant_name="Jane Doe",
            job_title="Data Scientist",
            company_name="DataCorp",
            email_body="Another test email",
            email_sender="jane@example.com"
        )

        # Test GET request
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['applications']), 2)
        self.assertEqual(data['total'], 2)

    @patch('services.job_applications.processor.JobApplicationProcessor.process_applications')
    def test_process_applications(self, mock_process):
        """Test processing and saving applications."""
        # Mock the processor response
        mock_process.return_value = [self.sample_email]

        # Test POST request
        response = self.client.post(self.url, {
            'query': 'subject:Application',
            'max_results': 10
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['applications']), 1)
        self.assertEqual(
            data['applications'][0]['applicant_name'],
            self.sample_email['applicant_name']
        )

        # Verify database
        self.assertEqual(JobApplication.objects.count(), 1)
        application = JobApplication.objects.first()
        self.assertEqual(application.applicant_name, "John Smith")
        self.assertEqual(application.job_title, "Software Engineer")

    @patch('services.job_applications.processor.JobApplicationProcessor.process_applications')
    def test_authentication_failure(self, mock_process):
        """Test handling of authentication failure."""
        # Mock authentication failure
        mock_process.return_value = None

        # Test POST request
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('Failed to authenticate', data['error'])

    def test_invalid_parameters(self):
        """Test handling of invalid parameters."""
        # Test invalid max_results
        response = self.client.post(self.url, {
            'max_results': 'invalid'
        })
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('Invalid parameters', data['error'])
