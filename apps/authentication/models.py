from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """Manager khusus untuk menangani pembuatan User menggunakan Email sebagai identifier."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email wajib diisi.")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", self.model.Role.SUPERUSER)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser harus memiliki is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser harus memiliki is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPERUSER = "SUPERUSER", "Superuser"
        ADMIN = "ADMIN", "Admin"
        GURU = "GURU", "Guru"
        SISWA = "SISWA", "Siswa"
        ORANGTUA = "ORANGTUA", "Orang Tua"

    # Menghapus kolom username bawaan Django
    username = None
    
    # Menjadikan email unik dan wajib
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.SISWA
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Tidak memerlukan field tambahan saat createsuperuser di CLI

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"