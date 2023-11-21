# accounts.views

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext as _
from rest_framework.decorators import action
from django.contrib.auth.hashers import check_password
from django.utils import timezone

from .models import UsersAuth
from . import serializers
from .permissions import IsOwnerSuperuser



class UserViewset(viewsets.ModelViewSet):

    """
    This view houses all users authentication methods:
    - Create new user
    - Verify new user email
    - Resend verification email
    - Change Password for logged in users
    - Reset password
    - Send reset paswword OTP
    - Login

    """

    queryset = UsersAuth.objects.all()
    serializer_class = serializers.UserSerializer
    search_fields = ('email', 'id')
    filterset_fields = ['is_deleted', 'is_staff']

    def get_serializer_class(self):
        if self.action == 'ResetPassword':
            return serializers.PasswordResetVerifiedSerializer
        if self.action == 'ResetPasswordTokenVerify':
            return serializers.PasswordResetVerifySerializer
        elif self.action == 'ChangePassword':
            return serializers.PasswordChangeSerializer
        elif self.action == 'Login':
            return serializers.LoginSerializer
        elif self.action == 'create':
            return serializers.NewUserSerializer
        elif self.action == 'SendPasswordOTP':
            return serializers.EmailSerializer

        return self.serializer_class
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ('update', 'partial_update', 'retrieve', 'ChangePassword'):
            permission_classes = [IsOwnerSuperuser]
        elif self.action == ('destroy', 'list'):
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        serializer.save()
        user = UsersAuth.objects.get(email=email)
        user.set_password(password)
        user.save()
        user.send_welcome_email()
                    
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(methods=['POST'], detail=False)
    def Login(self, request, format=None):
        serializer = self.get_serializer_class()(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(email=email, password=password)

            try:
                if user:
                    if user.is_active:
                        refresh = RefreshToken.for_user(user)
                        
                        data = {
                            'access': str(refresh.access_token),
                            'refresh': str(refresh),
                            'user_id': user.id
                        }
                        return Response(data, status=status.HTTP_200_OK)
                    else:
                        content = {'detail': _('User account not active.')}
                        return Response(content,
                                            status=status.HTTP_401_UNAUTHORIZED)
                else:
                    content = {'detail':
                            _('Unable to login with provided credentials.')}
                    return Response(content, status=status.HTTP_401_UNAUTHORIZED)
            
            except Exception as e:
                return Response({'detail': f'Unable to connect {e}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
            
    

    # Function to change password
    @action(methods=['POST'], detail=True)
    def ChangePassword(self, request, pk=None):
        serializer = self.get_serializer_class()(data=request.data, context={
            'request': request, 'id': pk})

        if serializer.is_valid():
            user = request.user

            password = serializer.validated_data['new_password']
            user.set_password(password)
            user.save()

            content = {'detail': _('Password changed.')}
            return Response(content, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


    # Function to initiate password reset
    @action(methods=['POST'], detail=False)
    def SendPasswordOTP(self, request, format=None):
        serializer = self.get_serializer_class()(data=request.data)

        if serializer.is_valid():
            email = serializer.data['email']

            try:
                user = UsersAuth.objects.get(email=email)

                if user.email_validation_status and user.is_active:
                    password_reset_code = user.create_password_reset()
                    user.send_password_reset_email(password_reset_code)
                    user.reset_token_creation_time = timezone.now()
                    user.save()
                    return Response({'detail': f'Password reset code sent to {email}'}, status=status.HTTP_201_CREATED)
                
                return Response({"detail": f"User is not verified"}, status=status.HTTP_400_BAD_REQUEST)

            except UsersAuth.DoesNotExist:
                pass

            # Since this is AllowAny, don't give away error.
            content = {'detail': _('Password reset not allowed.'), 'email': _(
                'Email address not found')}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    # Function to reset password
    @action(methods=['POST'], detail=False)
    def ResetPassword(self, request, format=None):
        serializer = self.get_serializer_class()(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            token = serializer.validated_data['token']
            password = serializer.validated_data['new_password']

            try:
                user = UsersAuth.objects.get(email=email)
                
                if not user.pass_reset_token:
                    return Response({'detail': 'No password reset request found for this user'}, status=status.HTTP_400_BAD_REQUEST)

                check = check_password(token, user.pass_reset_token)

                if check:

                    user.set_password(password)
                    user.pass_reset_token = None
                    user.save()

                    return Response({'detail': _('Password changed.')}, status=status.HTTP_200_OK)

                return Response({'detail': 'Token not valid'}, status=status.HTTP_400_BAD_REQUEST)

            except UsersAuth.DoesNotExist:
                return Response({'detail': 'Email not valid'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    # Function to verify reset password token
    @action(methods=['POST'], detail=False)
    def ResetPasswordTokenVerify(self, request, format=None):
        serializer = self.get_serializer_class()(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            token = serializer.validated_data['token']

            try:
                user = UsersAuth.objects.get(email=email)
                if not user.pass_reset_token:
                    return Response({'detail': "User does not have password reset request"}, status=status.HTTP_400_BAD_REQUEST)
                check = check_password(token, user.pass_reset_token)
                

                if check:
                    now = timezone.now()
                    token_time = user.reset_token_creation_time
                    expiry_time = ((now - token_time).seconds)/60
                    if expiry_time > 15:
                        return Response({'detail': 'Token expired'}, status=status.HTTP_403_FORBIDDEN)

                    return Response({'detail': _('Token confirmed.')}, status=status.HTTP_200_OK)

                return Response({'detail': 'Token not valid'}, status=status.HTTP_400_BAD_REQUEST)

            except UsersAuth.DoesNotExist:
                return Response({'detail': 'Email not valid'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)