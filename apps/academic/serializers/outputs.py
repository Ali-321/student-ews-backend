from django.db.models.aggregates import Avg, Max
from rest_framework import serializers
from academic.models import Kelas, MataPelajaran, Semester, Siswa, TahunAjaran
from assessment.models import NilaiSiswa, PredictionResult, PresensiSiswa
from authentication.serializers import UserListOutputSerializer


class TahunAjaranOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = TahunAjaran
        fields = ("id", "nama", "is_aktif")


class SemesterOutputSerializer(serializers.ModelSerializer):
    tahun_ajaran = TahunAjaranOutputSerializer(read_only=True)

    class Meta:
        model = Semester
        fields = ("id", "tahun_ajaran", "semester_ke", "is_aktif")


class KelasOutputSerializer(serializers.ModelSerializer):
    wali_kelas = UserListOutputSerializer(read_only=True)

    class Meta:
        model = Kelas
        fields = ("id", "nama_kelas", "wali_kelas")


class MataPelajaranOutputSerializer(serializers.ModelSerializer):
    pengajar = UserListOutputSerializer(read_only=True)

    class Meta:
        model = MataPelajaran
        fields = ("id", "kode_mapel", "nama_mapel", "pengajar")



class SiswaOutputSerializer(serializers.ModelSerializer):
  kelas = KelasOutputSerializer(read_only=True)
  parent_user = UserListOutputSerializer(read_only=True)
  presensi = serializers.SerializerMethodField()
  nilai = serializers.SerializerMethodField()
  status_risk = serializers.SerializerMethodField()

  class Meta:
    model = Siswa
    fields = (
        'nisn',
        'nama',
        'gender',
        'kelas',
        'parent_user',
        'presensi',
        'nilai',
        'status_risk',
    )

  def get_presensi(self, obj):
    p_total = PresensiSiswa.objects.filter(siswa=obj).count()
    p_hadir = PresensiSiswa.objects.filter(
        siswa=obj, status=PresensiSiswa.StatusChoices.HADIR
    ).count()
    return round((p_hadir / p_total * 100), 1) if p_total > 0 else 0.0

  def get_nilai(self, obj):
    avg_nilai = (
        NilaiSiswa.objects.filter(siswa=obj).aggregate(avg=Avg('skor'))['avg']
        or 0.0
    )
    return round(avg_nilai, 1)

  def get_status_risk(self, obj):
    student_risk_map = self.context.get('student_risk_map', {})
    # Default 'LOW' jika siswa belum ada record prediksi
    return student_risk_map.get(str(obj.pk), 'LOW')