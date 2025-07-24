from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.shortcuts import render
from datetime import timedelta
from .serializers import UserSignupSerializer, UserLoginSerializer
from .models import CustomUser
import logging

logger = logging.getLogger(__name__)



class SignupView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                
                remember_me = request.data.get('remember_me', False)
                if remember_me:
                    access_token.set_exp(lifetime=timedelta(days=1))
                else:
                    access_token.set_exp(lifetime=timedelta(minutes=15))
                
                response_data = {
                    'message': 'User registered successfully',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    },
                    'tokens': {
                        'access': str(access_token),
                        'refresh': str(refresh)
                    }
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': 'Validation failed',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Signup error: {str(e)}")
            return Response({
                'error': 'An error occurred during registration'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            remember_me = request.data.get('remember_me', False)
            
            if not username or not password:
                return Response({
                    'error': 'Username and password are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user = authenticate(username=username, password=password)
            
            if user is None:
                try:
                    user_obj = CustomUser.objects.get(username=username)
                    user_obj.failed_login_attempts += 1
                    
                    if user_obj.failed_login_attempts >= 5:
                        user_obj.account_locked_until = timezone.now() + timedelta(minutes=15)
                    
                    user_obj.save()
                except CustomUser.DoesNotExist:
                    pass
                
                return Response({
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            if user.account_locked_until and user.account_locked_until > timezone.now():
                return Response({
                    'error': 'Account is temporarily locked due to multiple failed login attempts'
                }, status=status.HTTP_423_LOCKED)
            
            user.failed_login_attempts = 0
            user.account_locked_until = None
            user.last_login = timezone.now()
            user.save()
            
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            if remember_me:
                access_token.set_exp(lifetime=timedelta(days=1))
            else:
                access_token.set_exp(lifetime=timedelta(minutes=15))
            
            response_data = {
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                },
                'tokens': {
                    'access': str(access_token),
                    'refresh': str(refresh)
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response({
                'error': 'An error occurred during login'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


