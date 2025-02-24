from django.urls import path
from .views import GmailAPI

urlpatterns = [
    path('emails/', GmailAPI.as_view(), name='gmail-emails'),
]
