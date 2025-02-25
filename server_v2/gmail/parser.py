"""Email parser for job applications.

This module provides functionality for parsing job application emails and extracting
relevant information such as applicant name, job title, and company name.
"""

import re
from typing import Dict, Optional, List, Tuple
from bs4 import BeautifulSoup
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailParser:
    """Parser for extracting job application information from emails."""

    # Regex patterns for extracting information
    PATTERNS = {
        'job_id': [
            r'job\s*(?:id|ref|reference|#):\s*([a-z0-9-_]+)',
            r'position\s*(?:id|ref|reference|#):\s*([a-z0-9-_]+)',
            r'req(?:uisition)?\s*(?:id|#):\s*([a-z0-9-_]+)',
        ],
        'applicant_name': [
            r'(?:candidate|applicant|name):\s*([a-zA-Z\s.]+)',
            r'application\s+(?:from|by):\s*([a-zA-Z\s.]+)',
            r'submitted\s+by:\s*([a-zA-Z\s.]+)',
        ],
        'job_title': [
            r'(?:position|job|role):\s*([a-zA-Z0-9\s]+(?:\s+developer|\s+engineer|\s+manager|\s+analyst|\s+designer|\s+consultant|\s+specialist|\s+coordinator|\s+director|\s+lead|\s+architect|\s+administrator|\s+technician|\s+supervisor)?)',
            r'applying\s+for:\s*([a-zA-Z0-9\s]+(?:\s+developer|\s+engineer|\s+manager|\s+analyst|\s+designer|\s+consultant|\s+specialist|\s+coordinator|\s+director|\s+lead|\s+architect|\s+administrator|\s+technician|\s+supervisor)?)',
        ],
        'company_name': [
            r'(?:company|organization|employer):\s*([a-zA-Z0-9\s&]+)',
            r'(?:at|with)\s+([a-zA-Z0-9\s&]+)\s+(?:company|organization|corp\.?|inc\.?|ltd\.?)',
        ],
    }

    # Field weights for confidence score calculation
    FIELD_WEIGHTS = {
        'applicant_name': 0.3,
        'job_title': 0.3,
        'company_name': 0.3,
        'job_id': 0.1,
    }

    # Minimum confidence thresholds for each field
    MIN_CONFIDENCE = {
        'applicant_name': 0.6,
        'job_title': 0.5,
        'company_name': 0.5,
        'job_id': 0.7,
    }

    def calculate_field_confidence(self, field: str, value: str, match_quality: float) -> float:
        """
        Calculate confidence score for a specific field based on various factors.
        
        Args:
            field: The field name (e.g., 'applicant_name')
            value: The extracted value
            match_quality: Quality of the regex match (0-1)
            
        Returns:
            float: Confidence score between 0 and 1
        """
        if not value:
            return 0.0

        base_score = match_quality

        # Length checks
        length = len(value.strip())
        if field == 'applicant_name':
            if 4 <= length <= 50 and ' ' in value:  # Likely first and last name
                base_score *= 1.2
            elif length < 4 or length > 50:
                base_score *= 0.5
        elif field == 'job_title':
            if 5 <= length <= 100:
                base_score *= 1.1
            elif length < 5 or length > 100:
                base_score *= 0.6
        elif field == 'company_name':
            if 2 <= length <= 50:
                base_score *= 1.1
            elif length > 50:
                base_score *= 0.7
        elif field == 'job_id':
            if 4 <= length <= 20 and any(c.isdigit() for c in value):
                base_score *= 1.2
            elif length < 4 or length > 20:
                base_score *= 0.6

        # Format checks
        if field == 'applicant_name':
            if re.match(r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)+$', value):  # Proper name format
                base_score *= 1.3
            if any(c.isdigit() for c in value):  # Names shouldn't contain numbers
                base_score *= 0.4

        elif field == 'job_title':
            common_terms = ['developer', 'engineer', 'manager', 'analyst', 'designer']
            if any(term in value.lower() for term in common_terms):
                base_score *= 1.2

        elif field == 'company_name':
            common_suffixes = ['Inc', 'LLC', 'Ltd', 'Corp', 'Limited']
            if any(suffix in value for suffix in common_suffixes):
                base_score *= 1.1

        # Normalize score to 0-1 range
        return min(max(base_score, 0.0), 1.0)

    def extract_field(self, text: str, patterns: List[str], field_name: str) -> Tuple[Optional[str], float]:
        """
        Extract a field using multiple regex patterns and return the best match with confidence.
        
        Args:
            text: Text to search in
            patterns: List of regex patterns
            field_name: Name of the field being extracted
            
        Returns:
            Tuple[Optional[str], float]: Extracted value and confidence score
        """
        best_match = None
        best_confidence = 0.0

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                value = match.group(1).strip()
                
                # Calculate match quality based on regex match
                match_quality = 0.7  # Base quality for a regex match
                
                # Adjust match quality based on pattern specificity
                if match.group(0).lower().startswith(field_name.split('_')[0]):
                    match_quality += 0.2  # Boost if pattern starts with field name
                
                # Calculate field-specific confidence
                confidence = self.calculate_field_confidence(field_name, value, match_quality)
                
                if confidence > best_confidence:
                    best_match = value
                    best_confidence = confidence

        return best_match, best_confidence

    def parse_email(self, email_data: Dict) -> Dict:
        """
        Parse email data to extract job application information.
        
        Args:
            email_data: Dictionary containing email data
            
        Returns:
            Dict: Extracted information with confidence scores
        """
        try:
            # Extract text content
            text = self._extract_text_content(email_data)
            
            # Initialize results
            results = {}
            confidence_scores = {}
            
            # Extract each field
            for field, patterns in self.PATTERNS.items():
                value, confidence = self.extract_field(text, patterns, field)
                results[field] = value
                confidence_scores[field] = confidence

            # Calculate overall confidence score
            overall_confidence = self._calculate_overall_confidence(confidence_scores)
            
            # Log extraction results
            logger.info(f"Extracted fields: {results}")
            logger.info(f"Confidence scores: {confidence_scores}")
            logger.info(f"Overall confidence: {overall_confidence}")

            return {
                'applicant_name': results.get('applicant_name'),
                'job_title': results.get('job_title'),
                'company_name': results.get('company_name'),
                'job_id': results.get('job_id'),
                'confidence_score': overall_confidence,
                'field_scores': confidence_scores,
            }

        except Exception as e:
            logger.error(f"Error parsing email: {str(e)}")
            raise

    def _extract_text_content(self, email_data: Dict) -> str:
        """
        Extract text content from email data, handling both HTML and plain text.
        
        Args:
            email_data: Dictionary containing email data
            
        Returns:
            str: Extracted text content
        """
        text = ""
        
        # Add subject
        if 'subject' in email_data:
            text += f"Subject: {email_data['subject']}\n"

        # Add sender
        if 'sender' in email_data:
            text += f"From: {email_data['sender']}\n"

        # Process body
        body = email_data.get('body', '')
        if body:
            # Check if body is HTML
            if '<html' in body.lower() or '<body' in body.lower():
                soup = BeautifulSoup(body, 'html.parser')
                text += soup.get_text(separator='\n')
            else:
                text += body

        return text

    def _calculate_overall_confidence(self, confidence_scores: Dict[str, float]) -> float:
        """
        Calculate overall confidence score based on individual field scores.
        
        Args:
            confidence_scores: Dictionary of field confidence scores
            
        Returns:
            float: Overall confidence score between 0 and 1
        """
        weighted_sum = 0
        total_weight = 0

        for field, score in confidence_scores.items():
            weight = self.FIELD_WEIGHTS.get(field, 0)
            min_confidence = self.MIN_CONFIDENCE.get(field, 0)
            
            # Penalize scores below minimum confidence
            if score < min_confidence:
                score *= 0.5
            
            weighted_sum += score * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        overall_score = weighted_sum / total_weight

        # Additional penalties for missing required fields
        required_fields = ['applicant_name', 'job_title', 'company_name']
        for field in required_fields:
            if confidence_scores.get(field, 0) < self.MIN_CONFIDENCE.get(field, 0):
                overall_score *= 0.7  # 30% penalty for each missing required field

        return round(min(max(overall_score, 0.0), 1.0), 2)
