from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import google.oauth2.credentials
import googleapiclient.discovery
import json

# Create your views here.

class GmailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get access token from request header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return Response({'error': 'No token provided'}, status=status.HTTP_401_UNAUTHORIZED)
            
            token = auth_header.split(' ')[1]

            # Create Gmail API service
            credentials = google.oauth2.credentials.Credentials(token)
            service = googleapiclient.discovery.build('gmail', 'v1', credentials=credentials)

            # Search for job-related emails
            query = 'subject:"job application" OR subject:"application status"'
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10
            ).execute()

            messages = results.get('messages', [])
            emails = []

            for message in messages:
                msg = service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()

                headers = msg['payload']['headers']
                email = {
                    'id': msg['id'],
                    'subject': next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject'),
                    'from': next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender'),
                    'date': next((h['value'] for h in headers if h['name'] == 'Date'), 'No Date'),
                }
                emails.append(email)

            return Response(emails)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
