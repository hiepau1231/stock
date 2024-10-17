from django.test import TestCase
from .models import CustomUser

class CustomUserTestCase(TestCase):
    def setUp(self):
        CustomUser.objects.create(username='testuser', password='testpass')

    def test_user_creation(self):
        user = CustomUser.objects.get(username='testuser')
        self.assertEqual(user.password, 'testpass')
