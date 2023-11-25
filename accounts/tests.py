# accounts.tests
from django.test import TestCase

from .models import UsersAuth


class AccountsModelsTestCase(TestCase):
    
    def test_user_data(self, email='user@test.com', password='test_password'):
        user = UsersAuth.objects.create(email=email, password=password)
        return user
    
    def test_user_registration(self):
        user = self.user_data()
        self.assertIsInstance(user, UsersAuth)
        self.assertEqual(user.__str__(), user.email)
        
    def test_user_authentication(self):
        pass