from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from academic.models import MataPelajaran, Semester, Siswa


class HistoriStudytime(models.Model):
    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE, related_name="studytime_history")
    mapel = models.ForeignKey(MataPelajaran, on_delete=models.CASCADE, related_name="studytime_history")
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name="studytime_history")
    minggu_ke = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(16)])
    studytime = models.IntegerField(help_text="Durasi belajar dalam jam per minggu")
    tanggal_input = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "assessment"
        db_table = "histori_studytime"
        ordering = ["minggu_ke"]
        constraints = [
            models.UniqueConstraint(
                fields=["siswa", "mapel", "semester", "minggu_ke"],
                name="unique_studytime_per_week"
            )
        ]
        indexes = [
            models.Index(fields=["siswa", "semester", "minggu_ke"]),
            models.Index(fields=["mapel", "semester"]),
        ]

    def __str__(self):
        return f"{self.siswa.nama} - {self.mapel.nama_mapel} (W{self.minggu_ke}: {self.studytime}h)"


class NilaiSiswa(models.Model):
    class EvaluasiChoices(models.TextChoices):
        QUIZ = "QUIZ", "Quiz"
        QUIZ2 = "QUIZ2", "Quiz2"
        TUGAS = "TUGAS", "Tugas"
        UTS = "UTS", "UTS"
        UAS = "UAS", "UAS"

    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE, related_name="nilai_list")
    mapel = models.ForeignKey(MataPelajaran, on_delete=models.CASCADE, related_name="nilai_list")
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name="nilai_list")
    minggu_ke = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(16)])
    jenis_evaluasi = models.CharField(max_length=10, choices=EvaluasiChoices.choices)
    nama_evaluasi = models.CharField(max_length=100)
    skor = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    is_terlambat = models.BooleanField(default=False)
    tanggal_input = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "assessment"
        db_table = "nilai_siswa"
        ordering = ["minggu_ke", "id"]
        indexes = [
            models.Index(fields=["siswa", "semester"]),
            models.Index(fields=["mapel", "semester", "jenis_evaluasi"]),
        ]

    def __str__(self):
        return f"{self.siswa.nama} - {self.mapel.kode_mapel} [{self.jenis_evaluasi}]: {self.skor}"


class PresensiSiswa(models.Model):
    class StatusChoices(models.TextChoices):
        HADIR = "Hadir", "Hadir"
        IZIN = "Izin", "Izin"
        SAKIT = "Sakit", "Sakit"
        ALPA = "Alpa", "Alpa"

    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE, related_name="presensi_list")
    mapel = models.ForeignKey(MataPelajaran, on_delete=models.CASCADE, related_name="presensi_list")
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name="presensi_list")
    minggu_ke = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(16)])
    tanggal = models.DateField()
    status = models.CharField(max_length=10, choices=StatusChoices.choices)

    class Meta:
        app_label = "assessment"
        db_table = "presensi_siswa"
        ordering = ["tanggal", "minggu_ke"]
        constraints = [
            models.UniqueConstraint(
                fields=["siswa", "mapel", "semester", "tanggal"],
                name="unique_presensi_per_day_mapel"
            )
        ]
        indexes = [
            models.Index(fields=["siswa", "semester", "status"]),
            models.Index(fields=["mapel", "semester", "minggu_ke"]),
        ]

    def __str__(self):
        return f"{self.siswa.nama} - {self.mapel.nama_mapel} (W{self.minggu_ke}): {self.status}"


class PredictionResult(models.Model):
    class RiskChoices(models.IntegerChoices):
        LOW = 0, "Low"
        MEDIUM = 1, "Medium"
        HIGH = 2, "High"

    siswa = models.ForeignKey(Siswa, on_delete=models.CASCADE, related_name="predictions")
    mapel = models.ForeignKey(MataPelajaran, on_delete=models.CASCADE, related_name="predictions")
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name="predictions")
    minggu_ke = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(16)])
    risk_score = models.IntegerField(choices=RiskChoices.choices)
    recommendation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "assessment"
        db_table = "prediction_result"
        ordering = ["-minggu_ke", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["siswa", "mapel", "semester", "minggu_ke"],
                name="unique_prediction_per_week"
            )
        ]
        indexes = [
            models.Index(fields=["siswa", "semester", "risk_score"]),
            models.Index(fields=["mapel", "semester", "risk_score"]),
        ]

    def __str__(self):
        return f"EWS {self.siswa.nama} - Mapel {self.mapel.kode_mapel} (W{self.minggu_ke}): Risk {self.get_risk_score_display()}"