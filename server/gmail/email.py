"""Gmail email service.

This module provides functionality for fetching and parsing emails from Gmail.
It handles email retrieval, content extraction, and parsing.
"""

import base64
import logging
import time
from typing import Dict, List, Optional, Union
from email.mime.text import MIMEText

from bs4 import BeautifulSoup
from googleapiclient.errors import HttpError

from .auth import GmailAuthService
from .parser import EmailParser
from .exceptions import (
    GmailAPIError,
    GmailAuthError,
    GmailNetworkError,
    GmailQuotaError,
    GmailRateLimitError,
)

# Configure logging
logger = logging.getLogger(__name__)

# Rate limiting constants
MAX_REQUESTS_PER_SECOND = 5
REQUEST_INTERVAL = 1.0 / MAX_REQUESTS_PER_SECOND


class GmailEmailService:
    """Service for handling Gmail email operations."""

    _last_request_time = 0
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds

    @classmethod
    def _rate_limit(cls):
        """Implement rate limiting for API requests."""
        current_time = time.time()
        time_since_last_request = current_time - cls._last_request_time
        if time_since_last_request < REQUEST_INTERVAL:
            time.sleep(REQUEST_INTERVAL - time_since_last_request)
        cls._last_request_time = time.time()

    @classmethod
    def fetch_emails(cls, query: str, max_results: int = 10, parse_content: bool = False) -> List[Dict]:
        """Fetch emails from Gmail API.

        Args:
            query: Gmail search query
            max_results: Maximum number of emails to fetch
            parse_content: Whether to parse email content for job details

        Returns:
            List of email dictionaries containing metadata and content
        """
        try:
            service = GmailAuthService.get_service()
            if not service:
                logger.error("Failed to get Gmail service")
                return []

            emails = []
            page_token = None
            remaining_results = max_results

            while remaining_results > 0:
                # Apply rate limiting
                cls._rate_limit()

                # Get list of messages
                try:
                    results = service.users().messages().list(
                        userId='me',
                        q=query,
                        maxResults=min(remaining_results, 100),  # Gmail API max is 100
                        pageToken=page_token
                    ).execute()
                except HttpError as e:
                    if e.resp.status == 429:  # Too Many Requests
                        logger.warning("Rate limit hit, waiting before retry")
                        time.sleep(5)  # Wait 5 seconds before retrying
                        continue
                    raise GmailAPIError(f"Gmail API error: {str(e)}", e.resp.status)

                messages = results.get('messages', [])
                if not messages:
                    break

                for message in messages:
                    try:
                        # Apply rate limiting for each message fetch
                        cls._rate_limit()

                        # Get full message details
                        msg = service.users().messages().get(
                            userId='me',
                            id=message['id'],
                            format='full'
                        ).execute()

                        # Extract email data
                        email_data = {
                            'id': msg['id'],
                            'thread_id': msg['threadId'],
                            'labels': msg['labelIds'],
                            'subject': cls._get_header_value(msg, 'Subject'),
                            'from': cls._get_header_value(msg, 'From'),
                            'to': cls._get_header_value(msg, 'To'),
                            'date': cls._get_header_value(msg, 'Date'),
                            'body': cls._get_body(msg)
                        }

                        # Parse content if requested
                        if parse_content:
                            parsed_data = EmailParser.parse_email(email_data)
                            email_data.update(parsed_data)

                        emails.append(email_data)
                        logger.debug("Successfully processed email %s", msg['id'])

                    except Exception as e:
                        logger.error("Error processing message %s: %s", message['id'], e)
                        continue

                # Update remaining results and page token
                remaining_results -= len(messages)
                page_token = results.get('nextPageToken')
                if not page_token:
                    break

            return emails

        except HttpError as error:
            raise GmailAPIError(f"Gmail API error: {str(error)}", error.resp.status)
        except Exception as e:
            logger.error('Error fetching emails: %s', e)
            return []

    @staticmethod
    def _get_header_value(message: Dict, header_name: str) -> str:
        """Extract header value from email message.

        Args:
            message: Email message dictionary
            header_name: Name of the header to extract

        Returns:
            Header value if found, empty string otherwise
        """
        headers = message.get('payload', {}).get('headers', [])
        for header in headers:
            if header['name'].lower() == header_name.lower():
                return header['value']
        return ''

    @classmethod
    def _get_body(cls, message: Dict) -> str:
        """Extract email body from message.

        Handles both plain text and HTML message parts.

        Args:
            message: Email message dictionary

        Returns:
            Email body text
        """
        try:
            parts = message.get('payload', {}).get('parts', [])
            if not parts:
                # Handle messages without parts
                data = message['payload'].get('body', {}).get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
                return ''

            # Try to find HTML part first, then fall back to plain text
            html_part = None
            text_part = None

            for part in parts:
                mime_type = part.get('mimeType', '')
                if mime_type == 'text/html':
                    html_part = part
                    break
                elif mime_type == 'text/plain':
                    text_part = part

            # Use HTML if available, otherwise use plain text
            part = html_part or text_part
            if not part:
                return ''

            data = part.get('body', {}).get('data', '')
            if not data:
                return ''

            return base64.urlsafe_b64decode(data).decode('utf-8')

        except Exception as e:
            logger.error("Error extracting email body: %s", e)
            return ''
