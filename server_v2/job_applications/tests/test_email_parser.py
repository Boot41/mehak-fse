"""Tests for email parsing functionality."""
import unittest
from ..utils.email_parser import EmailParser
from .data.sample_emails import (
    SAMPLE_HTML_EMAIL,
    SAMPLE_PLAIN_TEXT_EMAIL,
    SAMPLE_COMPLEX_EMAIL,
    SAMPLE_MINIMAL_EMAIL,
    SAMPLE_EDGE_CASE_EMAIL
)

class TestEmailParser(unittest.TestCase):
    """Test cases for EmailParser class."""
    
    def setUp(self):
        """Set up test environment."""
        self.parser = EmailParser()
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        text = "Test  Content"
        result = self.parser.clean_text(text)
        self.assertEqual(result, "Test Content")
    
    def test_extract_with_regex(self):
        """Test regex-based extraction."""
        result = self.parser.extract_with_regex(SAMPLE_PLAIN_TEXT_EMAIL)
        self.assertEqual(result['applicant_name'], "John Smith")
        self.assertEqual(result['position'], "Senior Software Engineer")
        self.assertEqual(result['company'], "Tech Corp")
        self.assertEqual(result['skills'], ["Python", "Java", "AWS", "REST APIs"])
        self.assertEqual(result['next_steps'], "Technical interview scheduled for next week")
    
    def test_parse_email_html(self):
        """Test parsing HTML emails."""
        result = self.parser.parse_email(SAMPLE_HTML_EMAIL)
        self.assertEqual(result['applicant_name'], "Mike Brown")
        self.assertEqual(result['position'], "Full Stack Developer")
        self.assertEqual(result['company'], "Tech Solutions Inc")
        self.assertEqual(result['skills'], ["Python", "React", "Node.js", "MongoDB"])
        self.assertEqual(result['next_steps'], "Technical interview scheduled for next Tuesday")
    
    def test_parse_email_plain_text(self):
        """Test parsing plain text emails."""
        result = self.parser.parse_email(SAMPLE_PLAIN_TEXT_EMAIL)
        self.assertEqual(result['applicant_name'], "John Smith")
        self.assertEqual(result['position'], "Senior Software Engineer")
        self.assertEqual(result['company'], "Tech Corp")
        self.assertEqual(result['skills'], ["Python", "Java", "AWS", "REST APIs"])
        self.assertEqual(result['next_steps'], "Technical interview scheduled for next week")
    
    def test_parse_email_complex(self):
        """Test parsing complex emails."""
        result = self.parser.parse_email(SAMPLE_COMPLEX_EMAIL)
        self.assertEqual(result['applicant_name'], "Sarah Johnson")
        self.assertEqual(result['position'], "Senior Data Scientist")
        self.assertEqual(result['company'], "Data Analytics Corp")
        self.assertEqual(result['skills'], ["Python", "R", "Machine Learning", "TensorFlow", "SQL", "Big Data"])
        self.assertEqual(result['next_steps'], "Team interview scheduled for Friday")
    
    def test_parse_email_minimal(self):
        """Test parsing minimal emails."""
        result = self.parser.parse_email(SAMPLE_MINIMAL_EMAIL)
        self.assertEqual(result['applicant_name'], "Alex Lee")
        self.assertEqual(result['position'], "Junior Developer")
        self.assertEqual(result['company'], "StartUp Tech")
        self.assertEqual(result['skills'], ["JavaScript"])
        self.assertEqual(result['next_steps'], "Phone screening")
    
    def test_parse_email_edge_cases(self):
        """Test parsing edge cases."""
        result = self.parser.parse_email(SAMPLE_EDGE_CASE_EMAIL)
        self.assertEqual(result, {
            'applicant_name': '',
            'position': '',
            'company': '',
            'skills': [],
            'next_steps': ''
        })
    
    def test_parse_email_empty(self):
        """Test parsing empty email."""
        result = self.parser.parse_email("")
        self.assertEqual(result, {
            'applicant_name': '',
            'position': '',
            'company': '',
            'skills': [],
            'next_steps': ''
        })

if __name__ == '__main__':
    unittest.main()
