from rest_framework import generics
from .serializers import UserSignupSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
from datetime import timedelta

class SignupView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        remember_me = request.data.get('remember_me', False)
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            if remember_me:
                # Set token lifetime to 1 day
                settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(days=1)
            else:
                settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(minutes=15)
        return response