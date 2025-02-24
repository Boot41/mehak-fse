from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from oauthlib.oauth2.rfc6749.errors import InsecureTransportError
from django.contrib.auth import get_user_model
import logging
from googleapiclient.discovery import build
from google.auth.exceptions import GoogleAuthError
import json
import traceback
import os
import sys

# Configure logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('''
Time: %(asctime)s
Logger: %(name)s
Level: %(levelname)s
File: %(filename)s
Line: %(lineno)d
Function: %(funcName)s
Message: %(message)s
''')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

User = get_user_model()

class GoogleAuthView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Handle Google OAuth callback
        """
        try:
            logger.info("\n=== Starting Google OAuth Callback Processing ===")
            logger.debug("Request Method: %s", request.method)
            logger.debug("Content Type: %s", request.content_type)
            logger.debug("Request Headers:")
            for header, value in request.headers.items():
                if header.lower() not in ['authorization', 'cookie']:  # Skip sensitive headers
                    logger.debug("  %s: %s", header, value)
            
            logger.debug("Request Data: %s", json.dumps(request.data, indent=2))
            
            code = request.data.get('code')
            if not code:
                logger.error("No authorization code provided in request")
                return Response(
                    {'error': 'Authorization code is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Verify client secrets file
            secrets_path = settings.GOOGLE_CLIENT_SECRETS_FILE
            logger.debug("Checking client secrets at: %s", secrets_path)
            
            if not os.path.exists(secrets_path):
                logger.error("Client secrets file not found at: %s", secrets_path)
                return Response(
                    {'error': 'OAuth configuration is missing', 'detail': 'Client secrets file not found'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Read and validate client secrets
            try:
                with open(secrets_path, 'r') as f:
                    secrets_content = json.load(f)
                logger.debug("Client secrets file loaded successfully")
                logger.debug("Client secrets content: %s", json.dumps(secrets_content, indent=2))
                
                # Validate required fields
                web_config = secrets_content.get('web', {})
                required_fields = ['client_id', 'client_secret', 'redirect_uris']
                missing_fields = [field for field in required_fields if not web_config.get(field)]
                
                if missing_fields:
                    logger.error("Missing required fields in client_secrets.json: %s", missing_fields)
                    return Response(
                        {'error': 'Invalid OAuth configuration', 'detail': f'Missing fields: {", ".join(missing_fields)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                logger.debug("Client secrets validation passed")
                logger.debug("Configured redirect URIs: %s", web_config['redirect_uris'])
                
            except json.JSONDecodeError as e:
                logger.error("Failed to parse client_secrets.json: %s", str(e))
                logger.error(traceback.format_exc())
                return Response(
                    {'error': 'Invalid OAuth configuration', 'detail': 'Client secrets file is not valid JSON'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except Exception as e:
                logger.error("Error reading client_secrets.json: %s", str(e))
                logger.error(traceback.format_exc())
                return Response(
                    {'error': 'Failed to load OAuth configuration', 'detail': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            try:
                logger.debug("\n=== Initializing OAuth Flow ===")
                logger.debug("Scopes: %s", settings.GOOGLE_OAUTH_SCOPES)
                logger.debug("Redirect URI: %s", settings.GOOGLE_OAUTH_REDIRECT_URI)
                
                # Allow HTTP for development
                os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
                
                flow = Flow.from_client_secrets_file(
                    secrets_path,
                    scopes=settings.GOOGLE_OAUTH_SCOPES,
                    redirect_uri=settings.GOOGLE_OAUTH_REDIRECT_URI
                )
                logger.debug("Flow initialized successfully")

                try:
                    logger.debug("\n=== Exchanging Authorization Code ===")
                    logger.debug("Code length: %d", len(code))
                    flow.fetch_token(code=code)
                    logger.debug("Token exchange successful")
                    
                except Exception as e:
                    logger.error("Token exchange failed: %s", str(e))
                    logger.error("Full traceback:\n%s", traceback.format_exc())
                    return Response(
                        {'error': 'Failed to exchange authorization code', 'detail': str(e)},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                credentials = flow.credentials
                logger.debug("\n=== Credentials Status ===")
                logger.debug("Token obtained: %s", bool(credentials.token))
                logger.debug("Token valid: %s", credentials.valid)
                logger.debug("Token expired: %s", credentials.expired)

                try:
                    logger.debug("\n=== Fetching User Info ===")
                    service = build('oauth2', 'v2', credentials=credentials)
                    user_info = service.userinfo().get().execute()
                    logger.debug("User info retrieved successfully")
                    logger.debug("User info: %s", json.dumps(user_info, indent=2))
                    
                except Exception as e:
                    logger.error("Failed to get user info: %s", str(e))
                    logger.error("Full traceback:\n%s", traceback.format_exc())
                    return Response(
                        {'error': 'Failed to get user info from Google', 'detail': str(e)},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                email = user_info.get('email')
                if not email:
                    logger.error("No email in user info")
                    logger.debug("Full user info: %s", json.dumps(user_info, indent=2))
                    return Response(
                        {'error': 'Email not provided by Google'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                try:
                    logger.debug("\n=== Creating/Updating User ===")
                    logger.debug("Email: %s", email)
                    user, created = User.objects.get_or_create(
                        email=email,
                        defaults={
                            'username': email,
                            'first_name': user_info.get('given_name', ''),
                            'last_name': user_info.get('family_name', ''),
                        }
                    )
                    logger.debug("User %s successfully", "created" if created else "retrieved")
                    
                except Exception as e:
                    logger.error("Database error: %s", str(e))
                    logger.error("Full traceback:\n%s", traceback.format_exc())
                    return Response(
                        {'error': 'Failed to create or update user', 'detail': str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                response_data = {
                    'access_token': credentials.token,
                    'refresh_token': credentials.refresh_token,
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    }
                }
                
                logger.debug("\n=== Sending Response ===")
                logger.debug("Response data structure:")
                logger.debug("  - access_token: %s", bool(response_data['access_token']))
                logger.debug("  - refresh_token: %s", bool(response_data['refresh_token']))
                logger.debug("  - user data present: %s", bool(response_data['user']))
                
                return Response(response_data)
                
            except Exception as flow_error:
                logger.error("\n=== Flow Error ===")
                logger.error("Error: %s", str(flow_error))
                logger.error("Full traceback:\n%s", traceback.format_exc())
                return Response(
                    {'error': 'OAuth flow error', 'detail': str(flow_error)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
        except Exception as e:
            logger.error("\n=== Unexpected Error ===")
            logger.error("Error: %s", str(e))
            logger.error("Full traceback:\n%s", traceback.format_exc())
            return Response(
                {'error': 'An unexpected error occurred', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
