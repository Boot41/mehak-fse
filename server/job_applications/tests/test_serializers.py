"""Test cases for job application serializers."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Application
from ..serializers import ApplicationSerializer

User = get_user_model()


class ApplicationSerializerTests(TestCase):
    """Test cases for ApplicationSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.application_data = {
            'applicant_name': 'John Doe',
            'job_title': 'Software Engineer',
            'company_name': 'Tech Corp',
            'status': 'applied',
            'email_content': 'Test application'
        }
        
        self.application = Application.objects.create(
            user=self.user,
            **self.application_data
        )
        
        self.serializer = ApplicationSerializer(instance=self.application)

    def test_contains_expected_fields(self):
        """Test that serializer contains expected fields."""
        data = self.serializer.data
        expected_fields = {
            'id',
            'user',
            'applicant_name',
            'job_title',
            'company_name',
            'status',
            'email_content',
            'created_at',
            'updated_at'
        }
        self.assertEqual(set(data.keys()), expected_fields)

    def test_applicant_name_field_content(self):
        """Test applicant_name field content."""
        data = self.serializer.data
        self.assertEqual(data['applicant_name'], self.application_data['applicant_name'])

    def test_job_title_field_content(self):
        """Test job_title field content."""
        data = self.serializer.data
        self.assertEqual(data['job_title'], self.application_data['job_title'])

    def test_company_name_field_content(self):
        """Test company_name field content."""
        data = self.serializer.data
        self.assertEqual(data['company_name'], self.application_data['company_name'])

    def test_status_field_content(self):
        """Test status field content."""
        data = self.serializer.data
        self.assertEqual(data['status'], self.application_data['status'])

    def test_email_content_field_content(self):
        """Test email_content field content."""
        data = self.serializer.data
        self.assertEqual(data['email_content'], self.application_data['email_content'])

    def test_serializer_with_invalid_status(self):
        """Test serializer with invalid status."""
        invalid_data = self.application_data.copy()
        invalid_data['status'] = 'invalid_status'
        serializer = ApplicationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)

    def test_serializer_with_empty_applicant_name(self):
        """Test serializer with empty applicant name."""
        invalid_data = self.application_data.copy()
        invalid_data['applicant_name'] = ''
        serializer = ApplicationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('applicant_name', serializer.errors)

    def test_serializer_with_empty_job_title(self):
        """Test serializer with empty job title."""
        invalid_data = self.application_data.copy()
        invalid_data['job_title'] = ''
        serializer = ApplicationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('job_title', serializer.errors)

    def test_serializer_with_empty_company_name(self):
        """Test serializer with empty company name."""
        invalid_data = self.application_data.copy()
        invalid_data['company_name'] = ''
        serializer = ApplicationSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('company_name', serializer.errors)

    def test_serializer_with_valid_data(self):
        """Test serializer with valid data."""
        serializer = ApplicationSerializer(data=self.application_data)
        self.assertTrue(serializer.is_valid())
