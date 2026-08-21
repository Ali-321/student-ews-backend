# apps/authentication/tests/test_selectors.py
from django.test import TestCase

from authentication.models import User
from authentication.selectors import user_get_me_selector


class AuthSelectorsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test_selector@example.com", 
            password="password"
        )

    def test_user_get_me_selector(self):
        # Memastikan selector mengembalikan instance user yang benar
        result = user_get_me_selector(user=self.user)
        self.assertEqual(result.email, self.user.email)
        self.assertEqual(result.id, self.user.id)