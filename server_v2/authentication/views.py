from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework import status, permissions
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
from .serializers import (
    UserSerializer,
    GoogleAuthSerializer,
    get_tokens_for_user
)
from google.oauth2 import id_token
from google.auth.transport import requests
from django.utils import timezone
from datetime import datetime, timedelta

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
    permission_classes = [permissions.AllowAny]
    serializer_class = GoogleAuthSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify the Google token
            user_data = serializer.validated_data['user_data']
            google_id = user_data['sub']
            email = user_data['email']

            # Create or update user
            user, created = User.objects.get_or_create(
                google_id=google_id,
                defaults={
                    'email': email,
                    'username': email,  # Using email as username
                    'first_name': user_data.get('given_name', ''),
                    'last_name': user_data.get('family_name', ''),
                    'profile_picture': user_data.get('picture', ''),
                }
            )

            if not created:
                # Update existing user's info
                user.first_name = user_data.get('given_name', user.first_name)
                user.last_name = user_data.get('family_name', user.last_name)
                user.profile_picture = user_data.get('picture', user.profile_picture)

            # Update tokens
            user.access_token = serializer.validated_data['access_token']
            user.token_expiry = timezone.now() + timedelta(hours=1)
            user.save()

            # Generate JWT tokens
            tokens = get_tokens_for_user(user)
            
            return Response({
                'tokens': tokens,
                'user': UserSerializer(user).data
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
