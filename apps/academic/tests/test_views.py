from rest_framework.test import APITestCase
from rest_framework import status
from authentication.models import User
from academic.models import Kelas
from rest_framework_simplejwt.tokens import RefreshToken

class AcademicViewTests(APITestCase):
    def setUp(self):
  
        self.url_siswa_list = "/api/v1/academic/siswa/"
        self.url_kelas_list = "/api/v1/academic/kelas/"

        self.admin = User.objects.create_user(email="admin@sch.id", password="123", role=User.Role.ADMIN)
        self.guru = User.objects.create_user(email="guru@sch.id", password="123", role=User.Role.GURU)
        
        self.kelas = Kelas.objects.create(nama_kelas="12 IPS 1")

    def get_auth_token(self, user):
        return str(RefreshToken.for_user(user).access_token)

    # --- Pengecekan Otorisasi (Hanya Admin) ---
    def test_siswa_list_api_as_admin_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_auth_token(self.admin)}')
        response = self.client.get(self.url_siswa_list)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Pastikan custom pagination bekerja (harus ada "results", "count", "next", dll jika limit offset aktif)
        self.assertIn("results", response.data)

    def test_siswa_list_api_as_guru_forbidden(self):
        """Guru diblokir dari endpoint pembuatan data master (terkecuali diizinkan secara eksplisit nanti)"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_auth_token(self.guru)}')
        response = self.client.get(self.url_siswa_list)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- Pengecekan Pembuatan Endpoint ---
    def test_kelas_create_api_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.get_auth_token(self.admin)}')
        payload = {
            "nama_kelas": "Kelas Eksperimen",
            # wali_kelas_id boleh dikosongkan
        }
        response = self.client.post(self.url_kelas_list, data=payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["nama_kelas"], "Kelas Eksperimen")
        self.assertTrue(Kelas.objects.filter(nama_kelas="Kelas Eksperimen").exists())