from rest_framework import serializers

# --- Sub-Serializers Insight Kelas ---
class InsightKelasItemSerializer(serializers.Serializer):
    nama_kelas = serializers.CharField()
    jumlah_siswa = serializers.IntegerField()


class InsightKelasSerializer(serializers.Serializer):
    high_risk_terbanyak = InsightKelasItemSerializer(many=True)
    low_risk_terbanyak = InsightKelasItemSerializer(many=True)


# --- Sub-Serializers Summary ---
class DashboardSummaryMetricsSerializer(serializers.Serializer):
    total_siswa = serializers.IntegerField()
    risiko_tinggi = serializers.IntegerField()
    risiko_sedang = serializers.IntegerField()
    rata_rata_presensi = serializers.FloatField()


class TrendPerformaItemSerializer(serializers.Serializer):
    minggu_ke = serializers.IntegerField()
    label = serializers.CharField()
    rata_rata_nilai = serializers.FloatField()
    rata_rata_presensi = serializers.FloatField()


class RiskDetailSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class ProporsiRisikoSerializer(serializers.Serializer):
    rendah = RiskDetailSerializer()
    sedang = RiskDetailSerializer()
    tinggi = RiskDetailSerializer()


class TopIntervensiItemSerializer(serializers.Serializer):
    nisn = serializers.CharField()
    nama = serializers.CharField()
    kelas = serializers.CharField()
    nilai = serializers.FloatField()
    kehadiran = serializers.FloatField()
    status_risk = serializers.CharField()


class DashboardDataContainerSerializer(serializers.Serializer):
    summary = DashboardSummaryMetricsSerializer()
    trend_performa = TrendPerformaItemSerializer(many=True)
    proporsi_risiko = ProporsiRisikoSerializer()
    insight_kelas = InsightKelasSerializer()
    top_intervensi = TopIntervensiItemSerializer(many=True)


class DashboardSummaryResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    data = DashboardDataContainerSerializer()


# --- Sub-Serializers Analytics ---
class KelasOptionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nama_kelas = serializers.CharField()


class MapelOptionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nama_mapel = serializers.CharField()


class FilterOptionsSerializer(serializers.Serializer):
    kelas = KelasOptionSerializer(many=True)
    mapel = MapelOptionSerializer(many=True)


# PENAMBAHAN MEDIUM DAN LOW RISK
class PerbandinganKelasItemSerializer(serializers.Serializer):
    nama_kelas = serializers.CharField()
    jumlah_high_risk = serializers.IntegerField()
    jumlah_medium_risk = serializers.IntegerField()
    jumlah_low_risk = serializers.IntegerField()


class FaktorRisikoItemSerializer(serializers.Serializer):
    faktor = serializers.CharField()
    percentage = serializers.FloatField()
    count = serializers.IntegerField()


class SchoolAnalyticsResponseDataSerializer(serializers.Serializer):
    filter_options = FilterOptionsSerializer()
    perbandingan_risiko_kelas = PerbandinganKelasItemSerializer(many=True)
    faktor_utama_risiko = FaktorRisikoItemSerializer(many=True)


class SchoolAnalyticsResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    data = SchoolAnalyticsResponseDataSerializer()


# --- Sub-Serializers Dashboard Siswa ---
class MapelAktifSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nama_mapel = serializers.CharField()

class PresensiHarianSerializer(serializers.Serializer):
    hari = serializers.CharField()
    status = serializers.CharField()

class NilaiMingguanSerializer(serializers.Serializer):
    tugas_1_pretest = serializers.FloatField(allow_null=True)
    tugas_2_posttest = serializers.FloatField(allow_null=True)
    assessment = serializers.FloatField(allow_null=True)

class RingkasanMingguanSerializer(serializers.Serializer):
    minggu_ke = serializers.IntegerField()
    study_time_jam = serializers.FloatField()
    presensi_harian = PresensiHarianSerializer(many=True)
    nilai = NilaiMingguanSerializer()

class AnalisisEWSSiswaSerializer(serializers.Serializer):
    status_risiko = serializers.CharField()
    label_risiko_display = serializers.CharField()
    rekomendasi = serializers.ListField(child=serializers.CharField())

class ProfilSiswaDashboardSerializer(serializers.Serializer):
    nisn = serializers.CharField()
    nama_siswa = serializers.CharField()
    kelas = serializers.CharField()

class DashboardSiswaDataSerializer(serializers.Serializer):
    profil = ProfilSiswaDashboardSerializer()
    mapel_aktif = MapelAktifSerializer()
    filter_opsi_mapel = MapelOptionSerializer(many=True) # Menggunakan yang sudah ada
    ringkasan_mingguan = RingkasanMingguanSerializer()
    analisis_ews = AnalisisEWSSiswaSerializer()

class DashboardSiswaResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    message = serializers.CharField()
    data = DashboardSiswaDataSerializer()


# --- Sub-Serializers Dashboard Orang Tua ---
class GrafikNilaiMingguanSerializer(serializers.Serializer):
    pretest = serializers.FloatField(allow_null=True)
    assessment = serializers.FloatField(allow_null=True)
    posttest = serializers.FloatField(allow_null=True)

class GrafikMingguanItemSerializer(serializers.Serializer):
    minggu_ke = serializers.IntegerField()
    label = serializers.CharField()
    presensi_persen = serializers.FloatField()
    study_time_jam = serializers.FloatField()
    nilai = GrafikNilaiMingguanSerializer()

class AnalisisEWSOrangTuaSerializer(serializers.Serializer):
    status_risiko = serializers.CharField()
    label_risiko_display = serializers.CharField()
    rekomendasi_orangtua = serializers.ListField(child=serializers.CharField())

class DashboardOrtuDataSerializer(serializers.Serializer):
    profil = ProfilSiswaDashboardSerializer()  
    mapel_aktif = MapelAktifSerializer()       
    filter_opsi_mapel = MapelOptionSerializer(many=True) 
    grafik_mingguan = GrafikMingguanItemSerializer(many=True)
    analisis_ews = AnalisisEWSOrangTuaSerializer()

class DashboardOrtuResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    message = serializers.CharField()
    data = DashboardOrtuDataSerializer()

    # --- Sub-Serializers Komparasi Bulanan ---
class KomparasiDetailSerializer(serializers.Serializer):
    sekarang = serializers.FloatField(allow_null=True)
    bulan_lalu = serializers.FloatField(allow_null=True)
    selisih = serializers.FloatField(allow_null=True)
    tren = serializers.CharField(allow_null=True)

class KomparasiBulananSerializer(serializers.Serializer):
    kehadiran = KomparasiDetailSerializer()
    study_time = KomparasiDetailSerializer()
    pretest = KomparasiDetailSerializer()
    assessment = KomparasiDetailSerializer()
    posttest = KomparasiDetailSerializer()

# --- Modifikasi Serializer Utama Ortu ---
class DashboardOrtuDataSerializer(serializers.Serializer):
    profil = ProfilSiswaDashboardSerializer()  
    mapel_aktif = MapelAktifSerializer() 
    filter_opsi_mapel = MapelOptionSerializer(many=True) 
    grafik_mingguan = GrafikMingguanItemSerializer(many=True)
    komparasi_bulanan = KomparasiBulananSerializer() # INJEKSI DATA BARU DI SINI
    analisis_ews = AnalisisEWSOrangTuaSerializer()