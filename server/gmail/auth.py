"""Gmail authentication service.

This module provides functionality for authenticating with the Gmail API using OAuth2.
It handles token management, refresh, and service creation.
"""

import logging
import os
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Configure logging
logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailAuthService:
    """Service for handling Gmail API authentication."""

    @classmethod
    def get_credentials(cls) -> Optional[Credentials]:
        """Get valid user credentials from storage.

        The file token.json stores the user's access and refresh tokens, and is
        created automatically when the authorization flow completes for the first time.

        Returns:
            Credentials object if successful, None otherwise.
        """
        creds = None
        token_path = Path("token.json")

        if token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
                logger.debug("Loaded existing credentials from %s", token_path)
            except Exception as e:
                logger.error("Error loading credentials: %s", e)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("Successfully refreshed credentials")
                except Exception as e:
                    logger.error("Error refreshing credentials: %s", e)
                    return None
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                    logger.info("Successfully completed OAuth2 flow")
                except FileNotFoundError:
                    logger.error("credentials.json not found. Download it from Google Cloud Console")
                    return None
                except Exception as e:
                    logger.error("Error in authentication flow: %s", e)
                    return None

            # Save the credentials for the next run
            try:
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                logger.debug("Saved credentials to %s", token_path)
            except Exception as e:
                logger.warning("Could not save token: %s", e)

        return creds

    @classmethod
    def get_service(cls):
        """Create a Gmail API service instance.

        Returns:
            Gmail API service instance if successful, None otherwise.
        """
        creds = cls.get_credentials()
        if not creds:
            logger.error("Failed to obtain credentials")
            return None

        try:
            service = build('gmail', 'v1', credentials=creds)
            logger.debug("Successfully created Gmail API service")
            return service
        except Exception as e:
            logger.error("Error building service: %s", e)
            return None
