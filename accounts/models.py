# accounts.models

import os
import sys
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext as _
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password

from .managers import UsersAuthManager
from .utils import send_multi_format_email

class UsersAuth(AbstractBaseUser, PermissionsMixin):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=200, unique=True)
    pass_reset_token = models.CharField(
        max_length=256, default=None, null=True, blank=True)
    reset_token_creation_time = models.DateTimeField(
        default=None, null=True, blank=True)
    date_time_created = models.DateTimeField(auto_now_add=True)
    date_time_modified = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(
        _('staff status'), default=False,
        help_text=_('Designates whether the user can log into the '
                    'admin site.'))

    USERNAME_FIELD = 'email'

    objects = UsersAuthManager()

    def __str__(self):
        return _(f"{self.email}")
    
    def create_password_reset(self):
        try:
            code = str(_generate_code())
            code = code[:5]
            hash_code = make_password(code)
            self.pass_reset_token = hash_code
            self.save()
        except:
            return False

        return code

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def create_password_reset(self):
        try:
            code = str(_generate_code())
            code = code[:5]
            hash_code = make_password(code)
            self.pass_reset_token = hash_code
            self.save()
        except:
            return False

        return code
    
    def send_password_reset_email(self, code):
        prefix = 'password_reset_email'
        self.send_email(prefix, code)

    def send_welcome_email(self):
        prefix = 'welcome_email'
        self.send_email(prefix)

    def send_email(self, prefix, code=None):
        ctxt = {
            'email': self.email,
            # 'name': f'{self.first_name}',
            'code': str(code)
        }
        send_multi_format_email(prefix, ctxt, target_email=self.email)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('All Users')
        # abstract = True


# Function to generate code for registration, password resets, email change
def _generate_code():
    # return binascii.hexlify(os.urandom(3)).decode('utf-8')
    return int.from_bytes(os.urandom(6), sys.byteorder)