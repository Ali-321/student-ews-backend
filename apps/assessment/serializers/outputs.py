from rest_framework import serializers
from assessment.models import HistoriStudytime, NilaiSiswa, PresensiSiswa, PredictionResult


class HistoriStudytimeOutputSerializer(serializers.ModelSerializer):
    siswa_nama = serializers.CharField(source="siswa.nama", read_only=True)
    mapel_nama = serializers.CharField(source="mapel.nama_mapel", read_only=True)

    class Meta:
        model = HistoriStudytime
        fields = ["id", "siswa", "siswa_nama", "mapel", "mapel_nama", "semester", "minggu_ke", "studytime", "tanggal_input"]

class StatusChoiceOutputSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()

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

class SiswaHybridRiskOutputSerializer(serializers.Serializer):
    nisn = serializers.CharField()
    nama_siswa = serializers.CharField(source="nama")
    kelas = serializers.CharField(source="kelas.nama_kelas", default="-")
    gender = serializers.CharField(default="-")
    presensi = serializers.SerializerMethodField()
    nilai = serializers.SerializerMethodField()
    status_risiko = serializers.SerializerMethodField()

    def get_presensi(self, obj) -> str:
        """Format angka menjadi string persentase (contoh: '85%')."""
        val = round(getattr(obj, "avg_presensi", 0.0), 1)
        return f"{int(val) if val.is_integer() else val}%"

    def get_nilai(self, obj) -> float:
        """Mengembalikan nilai rata-rata akademis."""
        return round(getattr(obj, "avg_predicted_score", 0.0), 1)

    def get_status_risiko(self, obj) -> str:
        """Mengubah enum kode internal ke bahasa Indonesia untuk UI Badge."""
        risk_map = {
            "HIGH": "Tinggi",
            "MEDIUM": "Sedang",
            "LOW": "Rendah",
        }
        status = getattr(obj, "risk_status", "LOW")
        return risk_map.get(status.upper(), status)