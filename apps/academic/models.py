from django.db import models
from authentication.models import User


class TahunAjaran(models.Model):
    nama = models.CharField(max_length=20)  # Contoh: "2025/2026"
    is_aktif = models.BooleanField(default=False)

    class Meta:
        app_label = "academic"
        db_table = "tahun_ajaran"

    def __str__(self):
        return self.nama


class Semester(models.Model):
    class SemesterChoices(models.IntegerChoices):
        GANJIL = 1, "Ganjil"
        GENAP = 2, "Genap"

    tahun_ajaran = models.ForeignKey(TahunAjaran, on_delete=models.CASCADE, related_name="semesters")
    semester_ke = models.IntegerField(choices=SemesterChoices.choices)
    is_aktif = models.BooleanField(default=False)

    class Meta:
        app_label = "academic"
        db_table = "semester"

    def __str__(self):
        return f"{self.tahun_ajaran.nama} - Semester {self.semester_ke}"


class Kelas(models.Model):
    nama_kelas = models.CharField(max_length=50)
    wali_kelas = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="kelas_wali",
        limit_choices_to={"role": User.Role.GURU},
    )

    class Meta:
        app_label = "academic"
        db_table = "kelas"

    def __str__(self):
        return self.nama_kelas


class MataPelajaran(models.Model):
    kode_mapel = models.CharField(max_length=20, unique=True)
    nama_mapel = models.CharField(max_length=100)
    pengajar = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mapel_diajar",
        limit_choices_to={"role": User.Role.GURU},
    )

    class Meta:
        app_label = "academic"
        db_table = "mata_pelajaran"

    def __str__(self):
        return f"{self.nama_mapel} ({self.kode_mapel})"


class Siswa(models.Model):
    class GenderChoices(models.TextChoices):
        LAKI_LAKI = "L", "Laki-laki"
        PEREMPUAN = "P", "Perempuan"

    nisn = models.CharField(max_length=20, primary_key=True)
    nama = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GenderChoices.choices)
    kelas = models.ForeignKey(Kelas, on_delete=models.CASCADE, related_name="siswa_list")
    parent_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="anak_list",
        limit_choices_to={"role": User.Role.ORANGTUA},
    )

    class Meta:
        app_label = "academic"
        db_table = "siswa"

    def __str__(self):
        return f"{self.nama} ({self.nisn})"