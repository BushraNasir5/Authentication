from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re

User = get_user_model()

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text='Password must be at least 8 characters long'
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    email = serializers.EmailField(
        required=True,
        help_text='Enter a valid email address'
    )
    first_name = serializers.CharField(
        max_length=30,
        required=True,
        help_text='Enter your first name'
    )
    last_name = serializers.CharField(
        max_length=30,
        required=True,
        help_text='Enter your last name'
    )
    username = serializers.CharField(
        max_length=150,
        required=True,
        help_text='Username can only contain letters, numbers, and underscores'
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'confirm_password']

    def validate_email(self, value):
        """
        Validate email format and uniqueness
        """
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address.")
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        
        return value

    def validate_username(self, value):
        """
        Validate username format and uniqueness
        """
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("Username can only contain letters, numbers, and underscores.")
        
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        
        return value

    def validate_password(self, value):
        """
        Validate password strength
        """
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        
        return value

    def validate(self, data):
        """
        Validate that passwords match
        """
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        """
        Create and return a new user instance
        """
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    remember_me = serializers.BooleanField(default=False, required=False)