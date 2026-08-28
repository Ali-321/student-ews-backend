from rest_framework import serializers
from assessment.models import NilaiSiswa, PresensiSiswa, PredictionResult


class HistoriStudytimeInputSerializer(serializers.Serializer):
    siswa_nisn = serializers.CharField(max_length=20)
    mapel_id = serializers.IntegerField()
    semester_id = serializers.IntegerField()
    minggu_ke = serializers.IntegerField(min_value=1, max_value=16)
    studytime = serializers.IntegerField(min_value=0)


class NilaiSiswaInputSerializer(serializers.Serializer):
    siswa_nisn = serializers.CharField(max_length=20)
    mapel_id = serializers.IntegerField()
    semester_id = serializers.IntegerField()
    minggu_ke = serializers.IntegerField(min_value=1, max_value=16)
    jenis_evaluasi = serializers.ChoiceField(choices=NilaiSiswa.EvaluasiChoices.choices)
    nama_evaluasi = serializers.CharField(max_length=100)
    skor = serializers.FloatField(min_value=0.0, max_value=100.0)
    is_terlambat = serializers.BooleanField(default=False)


class PresensiItemInputSerializer(serializers.Serializer):
    siswa_nisn = serializers.CharField(max_length=20)
    status = serializers.ChoiceField(choices=PresensiSiswa.StatusChoices.choices)


class BulkPresensiInputSerializer(serializers.Serializer):
    mapel_id = serializers.IntegerField()
    semester_id = serializers.IntegerField()
    minggu_ke = serializers.IntegerField(min_value=1, max_value=16)
    tanggal = serializers.DateField()
    items = PresensiItemInputSerializer(many=True)


class PredictionResultInputSerializer(serializers.Serializer):
    siswa_nisn = serializers.CharField(max_length=20)
    mapel_id = serializers.IntegerField()
    semester_id = serializers.IntegerField()
    minggu_ke = serializers.IntegerField(min_value=1, max_value=16)
    risk_score = serializers.ChoiceField(choices=PredictionResult.RiskChoices.choices)
    recommendation = serializers.CharField()