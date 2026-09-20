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


# ==========================================
# PREDICTION & RISK EWS SERIALIZERS
# ==========================================

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


# --- PERUBAHAN DI SINI: MENGGUNAKAN ATRIBUT MEMORI DARI SELECTOR ---
class SiswaHybridRiskOutputSerializer(serializers.Serializer):
    nisn = serializers.CharField()
    nama_siswa = serializers.CharField(source="nama")
    kelas = serializers.CharField(source="kelas.nama_kelas", default="-")
    gender = serializers.CharField(default="-")
    presensi = serializers.SerializerMethodField()
    nilai = serializers.SerializerMethodField()
    status_risiko = serializers.SerializerMethodField()

    def get_presensi(self, obj) -> str:
        return getattr(obj, "calc_presensi", "0%")

    def get_nilai(self, obj) -> float:
        return getattr(obj, "calc_nilai", 0.0)

    def get_status_risiko(self, obj) -> str:
        risk_map = {
            "HIGH": "Tinggi",
            "MEDIUM": "Sedang",
            "LOW": "Rendah",
        }
        status = getattr(obj, "calc_risk", "LOW")
        # PERBAIKAN: Cast ke string agar aman dari error integer
        status_str = str(status).upper()
        return risk_map.get(status_str, "Rendah")

class ProfilSiswaDetailSerializer(serializers.Serializer):
    nisn = serializers.CharField()
    nama_siswa = serializers.CharField()
    kelas = serializers.CharField()
    gender = serializers.CharField()

class MapelAktifDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nama_mapel = serializers.CharField()

class MetrikKinerjaSerializer(serializers.Serializer):
    kehadiran_pct = serializers.FloatField()
    study_hour = serializers.FloatField()
    rata_rata_tugas = serializers.FloatField()
    rata_rata_pretest = serializers.FloatField()
    rata_rata_posttest = serializers.FloatField()

class AnalisisEWSSerializer(serializers.Serializer):
    status_risiko = serializers.CharField()
    tingkat_risiko_display = serializers.CharField()
    rekomendasi_tindakan = serializers.CharField()

class SiswaRiskDetailDataSerializer(serializers.Serializer):
    profil_siswa = ProfilSiswaDetailSerializer()
    metrik_kinerja = MetrikKinerjaSerializer()
    mapel_aktif = MapelAktifDetailSerializer()
    analisis_ews = AnalisisEWSSerializer()

class SiswaRiskDetailResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    data = SiswaRiskDetailDataSerializer()