"""Test cases for job application models."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from ..models import Application

User = get_user_model()


class ApplicationModelTests(TestCase):
    """Test cases for Application model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.application = Application.objects.create(
            user=self.user,
            applicant_name='John Doe',
            job_title='Software Engineer',
            company_name='Tech Corp',
            status='applied',
            email_content='Test application'
        )

    def test_application_creation(self):
        """Test creating an application."""
        self.assertTrue(isinstance(self.application, Application))
        self.assertEqual(str(self.application),
                        'John Doe - Software Engineer at Tech Corp')

    def test_application_fields(self):
        """Test application fields."""
        self.assertEqual(self.application.user, self.user)
        self.assertEqual(self.application.applicant_name, 'John Doe')
        self.assertEqual(self.application.job_title, 'Software Engineer')
        self.assertEqual(self.application.company_name, 'Tech Corp')
        self.assertEqual(self.application.status, 'applied')
        self.assertEqual(self.application.email_content, 'Test application')

    def test_application_timestamps(self):
        """Test application timestamps."""
        self.assertTrue(isinstance(self.application.created_at, timezone.datetime))
        self.assertTrue(isinstance(self.application.updated_at, timezone.datetime))

    def test_application_status_choices(self):
        """Test application status choices."""
        valid_statuses = [choice[0] for choice in Application.STATUS_CHOICES]
        self.assertIn('applied', valid_statuses)
        self.assertIn('screening', valid_statuses)
        self.assertIn('interviewed', valid_statuses)
        self.assertIn('offer', valid_statuses)
        self.assertIn('accepted', valid_statuses)
        self.assertIn('rejected', valid_statuses)
        self.assertIn('ghosted', valid_statuses)

    def test_application_ordering(self):
        """Test application ordering."""
        Application.objects.create(
            user=self.user,
            applicant_name='Jane Smith',
            job_title='Data Scientist',
            company_name='AI Corp',
            status='screening',
            email_content='Test application 2'
        )
        applications = Application.objects.all()
        self.assertEqual(applications.count(), 2)
        self.assertTrue(applications[0].created_at >= applications[1].created_at)

    def test_application_user_cascade(self):
        """Test application deletion on user deletion."""
        self.assertEqual(Application.objects.count(), 1)
        self.user.delete()
        self.assertEqual(Application.objects.count(), 0)

    def test_application_update(self):
        """Test updating an application."""
        old_updated_at = self.application.updated_at
        self.application.status = 'screening'
        self.application.save()
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, 'screening')
        self.assertTrue(self.application.updated_at > old_updated_at)
