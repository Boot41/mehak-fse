from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'profile_picture')
        read_only_fields = ('id',)

class GoogleAuthSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=True)
    id_token = serializers.CharField(required=True)
    user_data = serializers.JSONField(required=True)

    def validate_user_data(self, value):
        required_fields = ['email', 'sub', 'given_name', 'family_name', 'picture']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Missing required field: {field}")
        return value

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['email'] = user.email
        token['google_id'] = user.google_id
        return token

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
