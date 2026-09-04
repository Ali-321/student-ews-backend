from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from academic.models import Kelas, Siswa
from authentication.models import User


class AcademicViewsTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(email="admin@school.id", password="password", role=User.Role.ADMIN)
        self.kelas = Kelas.objects.create(nama_kelas="10 IPA 1")
        self.siswa = Siswa.objects.create(
            nisn="1001",
            nama="Budi",
            gender="L",
            kelas=self.kelas,
        )

    def test_get_siswa_list_paginated(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse("academic:siswa_list_create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_siswa(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(reverse("academic:siswa_detail", kwargs={"nisn": self.siswa.nisn}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)