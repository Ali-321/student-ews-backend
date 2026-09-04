from rest_framework import serializers
from academic.models import Semester, Siswa


# --- TAHUN AJARAN ---
class TahunAjaranInputSerializer(serializers.Serializer):
    nama = serializers.CharField(max_length=20)
    is_aktif = serializers.BooleanField(default=False)


class TahunAjaranUpdateSerializer(serializers.Serializer):
    nama = serializers.CharField(max_length=20, required=False)
    is_aktif = serializers.BooleanField(required=False)


# --- SEMESTER ---
class SemesterInputSerializer(serializers.Serializer):
    tahun_ajaran_id = serializers.IntegerField()
    semester_ke = serializers.ChoiceField(choices=Semester.SemesterChoices.choices)
    is_aktif = serializers.BooleanField(default=False)


class SemesterUpdateSerializer(serializers.Serializer):
    tahun_ajaran_id = serializers.IntegerField(required=False)
    semester_ke = serializers.ChoiceField(choices=Semester.SemesterChoices.choices, required=False)
    is_aktif = serializers.BooleanField(required=False)


# --- KELAS ---
class KelasInputSerializer(serializers.Serializer):
    nama_kelas = serializers.CharField(max_length=50)
    wali_kelas_id = serializers.IntegerField(required=False, allow_null=True)


class KelasUpdateSerializer(serializers.Serializer):
    nama_kelas = serializers.CharField(max_length=50, required=False)
    wali_kelas_id = serializers.IntegerField(required=False, allow_null=True)


# --- MATA PELAJARAN ---
class MataPelajaranInputSerializer(serializers.Serializer):
    kode_mapel = serializers.CharField(max_length=20)
    nama_mapel = serializers.CharField(max_length=100)
    pengajar_id = serializers.IntegerField(required=False, allow_null=True)


class MataPelajaranUpdateSerializer(serializers.Serializer):
    kode_mapel = serializers.CharField(max_length=20, required=False)
    nama_mapel = serializers.CharField(max_length=100, required=False)
    pengajar_id = serializers.IntegerField(required=False, allow_null=True)


# --- SISWA ---
class SiswaInputSerializer(serializers.Serializer):
    nisn = serializers.CharField(max_length=20)
    nama = serializers.CharField(max_length=100)
    gender = serializers.ChoiceField(choices=Siswa.GenderChoices.choices)
    kelas_id = serializers.IntegerField()
    parent_user_id = serializers.IntegerField(required=False, allow_null=True)


class SiswaUpdateSerializer(serializers.Serializer):
    nama = serializers.CharField(max_length=100, required=False)
    gender = serializers.ChoiceField(choices=Siswa.GenderChoices.choices, required=False)
    kelas_id = serializers.IntegerField(required=False)
    parent_user_id = serializers.IntegerField(required=False, allow_null=True)