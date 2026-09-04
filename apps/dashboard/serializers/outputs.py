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


class PerbandinganKelasItemSerializer(serializers.Serializer):
  nama_kelas = serializers.CharField()
  jumlah_high_risk = serializers.IntegerField()


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