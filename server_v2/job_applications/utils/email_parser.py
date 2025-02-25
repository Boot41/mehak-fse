"""Email parsing utilities."""
import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup


class EmailParser:
    """Parse emails to extract job application information."""
    
    EMPTY_RESULT = {
        'applicant_name': '',
        'position': '',
        'company': '',
        'skills': [],
        'next_steps': ''
    }
    
    def __init__(self):
        """Initialize the email parser."""
        self.patterns = {
            'position': [
                r'Position:\s*([^:\n]+)',
                r'Job Title:\s*([^:\n]+)',
                r'Role:\s*([^:\n]+)',
                r'(?i)position.*?(?:for|of)\s+([^:\n,]+)',
                r'(?i)applying for.*?position.*?of\s+([^:\n,]+)'
            ],
            'company_name': [
                r'Company:\s*([^:\n]+)',
                r'Organization:\s*([^:\n]+)',
                r'(?i)position at\s+([^:\n,]+)',
                r'(?i)role at\s+([^:\n,]+)',
                r'(?i)job.*?at\s+([^:\n,]+)'
            ]
        }
    
    def parse_email(self, email_body: str, email_subject: str = '') -> dict:
        """Parse email content for job details.
        
        Args:
            email_body: The body of the email
            email_subject: The email subject line
            
        Returns:
            dict: Extracted job details
        """
        # Clean and combine text
        text = email_body or ''
        if email_subject:
            text = f"{email_subject}\n\n{text}"
            
        # Remove HTML tags if present
        if '<' in text and '>' in text:
            soup = BeautifulSoup(text, 'html.parser')
            text = soup.get_text()
        
        # Fix common formatting issues
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')
        
        # Normalize whitespace
        lines = text.split('\n')
        lines = [re.sub(r'\s+', ' ', line.strip()) for line in lines]
        text = '\n'.join(line for line in lines if line)
        
        # Extract information
        details = {
            'position': '',
            'company_name': ''
        }
        
        # Try each pattern for position and company
        for field, pattern_list in self.patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text)
                if match:
                    details[field] = match.group(1).strip()
                    break
        
        # If no position found in patterns, try to extract from subject
        if not details['position'] and email_subject:
            # Common position keywords
            keywords = ['Engineer', 'Developer', 'Manager', 'Analyst', 'Designer']
            for keyword in keywords:
                if keyword.lower() in email_subject.lower():
                    position = re.search(fr'.*?({keyword}[^\n,]*)', email_subject, re.I)
                    if position:
                        details['position'] = position.group(1).strip()
                        break
        
        return details
