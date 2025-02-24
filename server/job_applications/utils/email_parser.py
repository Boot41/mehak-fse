"""Email parsing utilities."""
import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import openai

class EmailParser:
    """Parse emails to extract job application information."""
    
    def __init__(self):
        """Initialize parser with regex patterns."""
        self.patterns = {
            'applicant_name': r'Name:\s*([^:\n]+)',
            'position': r'Position:\s*([^:\n]+)',
            'company': r'Company:\s*([^:\n]+)',
            'skills': r'Skills:\s*([^:\n]+)',
            'next_steps': r'Next Steps:\s*([^:\n]+)'
        }
    
    def clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace and normalizing newlines."""
        if not text:
            return ""
            
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
        
        return text
    
    def extract_with_regex(self, text: str) -> Dict[str, str]:
        """Extract information using regex patterns."""
        result = {}
        for key, pattern in self.patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                if key == 'skills':
                    # Split skills into a list
                    result[key] = [s.strip() for s in value.split(',')]
                else:
                    result[key] = value
            else:
                result[key] = '' if key != 'skills' else []
        return result
    
    def extract_with_openai(self, text: str) -> Dict[str, str]:
        """Extract information using OpenAI API."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract the following information from the job application email: applicant name, position, company, skills (as a list), and next steps. Return the information in JSON format."},
                    {"role": "user", "content": text}
                ]
            )
            
            # Parse OpenAI response
            content = response.choices[0].message.content
            try:
                import json
                result = json.loads(content)
                # Ensure all required fields are present
                required_fields = ['applicant_name', 'position', 'company', 'skills', 'next_steps']
                for field in required_fields:
                    if field not in result:
                        result[field] = '' if field != 'skills' else []
                return result
            except json.JSONDecodeError:
                return self._empty_result()
        except Exception:
            return self._empty_result()
    
    def parse_email(self, email_text: str, use_openai: bool = False) -> Dict:
        """Parse email content to extract job application information."""
        # Clean the text
        text = self.clean_text(email_text)
        
        # Try regex extraction first
        result = self.extract_with_regex(text)
        
        # If regex fails or OpenAI is requested, try OpenAI
        if use_openai or not any(result.values()):
            openai_result = self.extract_with_openai(text)
            if any(openai_result.values()):
                result = openai_result
        
        # Ensure all fields are present
        required_fields = {
            'applicant_name': '',
            'position': '',
            'company': '',
            'skills': [],
            'next_steps': ''
        }
        return {**required_fields, **result}
    
    def _empty_result(self) -> Dict:
        """Return an empty result with all required fields."""
        return {
            'applicant_name': '',
            'position': '',
            'company': '',
            'skills': [],
            'next_steps': ''
        }
