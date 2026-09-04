from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class DashboardViewsTestCase(APITestCase):

    def setUp(self):
        # Buat User Guru (menggunakan Email & Role Enum)
        self.guru_user = User.objects.create_user(
            email='guru1@example.com',
            password='Password123!',
            role=User.Role.GURU,
        )
        # Buat User Non-Guru (Siswa)
        self.other_user = User.objects.create_user(
            email='siswa1@example.com',
            password='Password123!',
            role=User.Role.SISWA,
        )

        self.summary_url = reverse('dashboard:dashboard-summary')
        self.analytics_url = reverse('dashboard:dashboard-analytics')

    def test_unauthenticated_access_denied(self):
        # Tanpa autentikasi
        response = self.client.get(self.summary_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_teacher_role_forbidden(self):
        # Login sebagai non-guru (Siswa)
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.summary_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_dashboard_summary_view_success(self):
        # Authenticate sebagai Guru
        self.client.force_authenticate(user=self.guru_user)
        response = self.client.get(self.summary_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIn('summary', response.data['data'])

    def test_dashboard_analytics_view_with_params_success(self):
        self.client.force_authenticate(user=self.guru_user)
        response = self.client.get(
            self.analytics_url, {'kelas_id': '1', 'mapel_id': '1'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('filter_options', response.data['data'])
        self.assertIn('faktor_utama_risiko', response.data['data'])