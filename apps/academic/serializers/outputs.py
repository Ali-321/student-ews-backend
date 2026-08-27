from rest_framework import serializers
from academic.models import Kelas, MataPelajaran, Semester, Siswa, TahunAjaran
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

    class Meta:
        model = Siswa
        fields = ("nisn", "nama", "gender", "angkatan", "kelas", "parent_user")