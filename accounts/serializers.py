# accounts.serializers

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError
from django.core import exceptions
import django.contrib.auth.password_validation as validators

from .models import UsersAuth


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UsersAuth
        fields = ('id', 'email', 'date_time_created', 'date_time_modified', 'is_deleted')
        read_only_fields = ('id', 'date_time_created', 'date_time_modified', 'is_deleted', 'email')

class NewUserSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(max_length=128, write_only=True, required=True, 
        label = 'Password',
        style={'input_type': 'password', 'placeholder': 'Password'})
    
    re_password = serializers.CharField(max_length=128, write_only=True, required=True, 
        label = 'Password again',
        style={'input_type': 'password', 'placeholder': 'Password'})
    
    class Meta:
        model = UsersAuth
        fields = ('id', 'email', 'password', 're_password', 'date_time_created', 'date_time_modified')
        read_only_fields = ('id', 'date_time_created', 'date_time_modified')

    def validate(self, attrs):        
        
        user = UsersAuth(**attrs)
         
        # get the password from the data
        password = attrs.get('password')
        password2 = attrs.pop('re_password')

        errors = dict() 
        
        if password != password2:
            errors['password']='Passwords do not match'
            errors['re_password']='Passwords do not match'
        
        try:
            user = UsersAuth.objects.get(email=attrs.get('email'))
            if user:
                errors['email']='Email address already taken.'
        except UsersAuth.DoesNotExist:
            pass
        
        try:
            # validate the password and catch the exception
            validators.validate_password(password=password, user=user)
        
        # the exception raised here is different than serializers.ValidationError
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)
        return super().validate(attrs)
    
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True, required=True, 
        label = 'Password',
        style={'input_type': 'password', 'placeholder': 'Password'})
    
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    user_id = serializers.CharField(read_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        
        user = UsersAuth.objects.filter(email=email).first()
        
        if user is None:
            raise serializers.ValidationError({"email": "Invalid Email"})
        else:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError({"password": 'Incorrect password, check and try again'})

        return super().validate(attrs)
    
class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    
    def validate(self, attrs):
        email = attrs.get('email', '')
        
        user = UsersAuth.objects.filter(email=email).first()

        if user is None:
            raise serializers.ValidationError({"email": "Invalid Email"})
        return super().validate(attrs)


class PasswordResetVerifySerializer(serializers.Serializer):
    
    email = serializers.EmailField(max_length=255)
    token = serializers.IntegerField(write_only=True, required=True, label='Verification token')

    def validate(self, attrs):
        email = attrs.get('email', '')
        
        user = UsersAuth.objects.filter(email=email).first()

        if user is None:
            raise serializers.ValidationError({"email": "Invalid Email"})

        return super().validate(attrs)


class PasswordResetVerifiedSerializer(serializers.Serializer):
    
    email = serializers.EmailField(max_length=255)
    token = serializers.IntegerField(write_only=True, required=True, label='Verification token')
    new_password = serializers.CharField(max_length=128, write_only=True, required=True, 
        label = 'New Password',
        style={'input_type': 'password', 'placeholder': 'Password'})
    
    re_new_password = serializers.CharField(max_length=128, write_only=True, required=True, 
        label = 'New Password again',
        style={'input_type': 'password', 'placeholder': 'New Password'})
    
    def validate(self, attrs):
        
        email = attrs.get('email', '')
        
        user = UsersAuth.objects.filter(email=email).first()

        if user is None:
            raise serializers.ValidationError({"email": "Invalid Email"})

        # get the password from the data
        password = attrs.get('new_password')
        password2 = attrs.pop('re_new_password')
        
        errors = dict()
        
        if password != password2:
            errors['password']='Passwords do not match'
            errors['re_password']='Passwords do not match'
        
        try:
            # validate the password and catch the exception
            validators.validate_password(password=password, user=user)
        
        # the exception raised here is different than serializers.ValidationError
        except exceptions.ValidationError as e:
            errors['new_password'] = list(e.messages)
        
        if errors:
            raise serializers.ValidationError(errors)
        
        
        attrs.pop('re_new_password')
        return super().validate(attrs)


class PasswordChangeSerializer(serializers.Serializer):
    # user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    old_password = serializers.CharField(max_length=128, write_only=True, required=True, 
        label = 'Old Password',
        style={'input_type': 'password', 'placeholder': 'Old Password'})

    new_password = serializers.CharField(max_length=128, write_only=True, required=True, 
        label = 'New Password',
        style={'input_type': 'password', 'placeholder': 'New Password'})

    re_new_password = serializers.CharField(max_length=128, write_only=True, required=True, 
        label = 'New Password again',
        style={'input_type': 'password', 'placeholder': 'New Password'})
    
    
    def validate(self, attrs):
        password = attrs.get('old_password', '')
        new_password = attrs.get('new_password', '')
        password2 = attrs.pop('re_new_password')
        get_user = UsersAuth.objects.get(id=self.context.get("id"))
        user = authenticate(email=get_user.email, password=password)
        
        errors = dict()
        
        if not user:
            errors['old_password']='Incorrect password, check and try again'
        if password == new_password:            
            errors['new_password']=['Passwords do not match']

        
        if new_password != password2:
            errors['new_password'] = errors['new_password'].append('Passwords do not match') if 'new_password' in errors else 'Passwords do not match'
            errors['re_new_password']='Passwords do not match'
        try:
            # validate the password and catch the exception
            validators.validate_password(password=new_password, user=user)
        
        # the exception raised here is different than serializers.ValidationError
        except exceptions.ValidationError as e:
            errors['new_password'] = errors['new_password']+list(e.messages) if 'new_password' in errors else list(e.messages)
        
        if errors:
            raise serializers.ValidationError(errors)
        
        attrs.pop('re_new_password')
        
        return super().validate(attrs)
