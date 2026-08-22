# apps/authentication/tests/test_selectors.py
from django.test import TestCase

from authentication.models import User
from authentication.selectors import (user_get_me_selector, user_list_selector)





class AuthSelectorsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test_selector@example.com", 
            password="password"
        )

    def test_user_get_me_selector(self):

        result = user_get_me_selector(user=self.user)
        self.assertEqual(result.email, self.user.email)
        self.assertEqual(result.id, self.user.id)
        
    def test_user_list_selector_returns_all(self):
        """Memastikan selector mengembalikan seluruh daftar user."""
        User.objects.create_user(email="user2@example.com", password="password")

        users = user_list_selector()
        self.assertEqual(users.count(), 2)  # 1 dari setUp() + 1 user2


    def test_user_list_selector_filter_by_role(self):
        """Memastikan selector berhasil memfilter user berdasarkan query role."""
        User.objects.create_user(
            email="guru@school.id", password="password", role=User.Role.GURU
        )

        guru_users = user_list_selector(role=User.Role.GURU)
        self.assertEqual(guru_users.count(), 1)
        self.assertEqual(guru_users.first().email, "guru@school.id")
