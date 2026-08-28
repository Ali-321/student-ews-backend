from rest_framework import serializers
from assessment.models import HistoriStudytime, NilaiSiswa, PresensiSiswa, PredictionResult


class HistoriStudytimeOutputSerializer(serializers.ModelSerializer):
    siswa_nama = serializers.CharField(source="siswa.nama", read_only=True)
    mapel_nama = serializers.CharField(source="mapel.nama_mapel", read_only=True)

    class Meta:
        model = HistoriStudytime
        fields = ["id", "siswa", "siswa_nama", "mapel", "mapel_nama", "semester", "minggu_ke", "studytime", "tanggal_input"]


class NilaiSiswaOutputSerializer(serializers.ModelSerializer):
    siswa_nama = serializers.CharField(source="siswa.nama", read_only=True)
    mapel_kode = serializers.CharField(source="mapel.kode_mapel", read_only=True)
    mapel_nama = serializers.CharField(source="mapel.nama_mapel", read_only=True)

    class Meta:
        model = NilaiSiswa
        fields = [
            "id", "siswa", "siswa_nama", "mapel", "mapel_kode", "mapel_nama",
            "semester", "minggu_ke", "jenis_evaluasi", "nama_evaluasi",
            "skor", "is_terlambat", "tanggal_input"
        ]


class PresensiSiswaOutputSerializer(serializers.ModelSerializer):
    siswa_nama = serializers.CharField(source="siswa.nama", read_only=True)
    mapel_nama = serializers.CharField(source="mapel.nama_mapel", read_only=True)

    class Meta:
        model = PresensiSiswa
        fields = ["id", "siswa", "siswa_nama", "mapel", "mapel_nama", "semester", "minggu_ke", "tanggal", "status"]


class PredictionResultOutputSerializer(serializers.ModelSerializer):
    siswa_nama = serializers.CharField(source="siswa.nama", read_only=True)
    mapel_nama = serializers.CharField(source="mapel.nama_mapel", read_only=True)
    risk_display = serializers.CharField(source="get_risk_score_display", read_only=True)

    class Meta:
        model = PredictionResult
        fields = [
            "id", "siswa", "siswa_nama", "mapel", "mapel_nama", "semester",
            "minggu_ke", "risk_score", "risk_display", "recommendation", "created_at"
        ]