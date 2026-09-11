from rest_framework import serializers
from assessment.models import NilaiSiswa, PresensiSiswa, PredictionResult


class HistoriStudytimeInputSerializer(serializers.Serializer):
    siswa_nisn = serializers.CharField(max_length=20)
    mapel_id = serializers.IntegerField()
    semester_id = serializers.IntegerField()
    minggu_ke = serializers.IntegerField(min_value=1, max_value=16)
    studytime = serializers.IntegerField(min_value=0)

# --- Presensi Grid (Multi-Hari / Periode) ---
class PresensiHarianSerializer(serializers.Serializer):
    tanggal = serializers.DateField()
    status = serializers.ChoiceField(choices=PresensiSiswa.StatusChoices.choices)

class SiswaPresensiGridSerializer(serializers.Serializer):
    siswa_nisn = serializers.CharField(max_length=20)
    presensi_harian = PresensiHarianSerializer(many=True)

class BulkPresensiInputSerializer(serializers.Serializer):
    mapel_id = serializers.IntegerField()
    semester_id = serializers.IntegerField()
    tanggal_mulai = serializers.DateField()
    tanggal_akhir = serializers.DateField()
    items = SiswaPresensiGridSerializer(many=True)


# --- Assessment Matrix (Study Time + Multiple Evaluasi) ---
class EvaluasiItemSerializer(serializers.Serializer):
    jenis_evaluasi = serializers.ChoiceField(choices=NilaiSiswa.EvaluasiChoices.choices)
    nama_evaluasi = serializers.CharField(max_length=100)
    skor = serializers.FloatField(
        min_value=0.0,
        max_value=100.0,
        required=True,
        allow_null=False,
        error_messages={
            "null": "Skor nilai tidak boleh kosong.",
            "required": "Skor nilai wajib diisi.",
        },
    )

class SiswaAssessmentItemSerializer(serializers.Serializer):
    siswa_nisn = serializers.CharField(max_length=20)
    studytime = serializers.IntegerField(
        min_value=0,
        required=True,
        allow_null=False,
        error_messages={
            "null": "Study time tidak boleh kosong.",
            "required": "Study time wajib diisi.",
        },
    )
    evaluasi_list = EvaluasiItemSerializer(many=True, required=True, allow_empty=False)

class BulkAssessmentInputSerializer(serializers.Serializer):
    mapel_id = serializers.IntegerField()
    semester_id = serializers.IntegerField()
    tanggal_input = serializers.DateField()
    items = SiswaAssessmentItemSerializer(many=True, required=True, allow_empty=False)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Daftar siswa tidak boleh kosong.")

        # Ambil struktur kolom evaluasi dari siswa pertama sebagai acuan/matriks
        ref_eval_keys = {
            (e["jenis_evaluasi"], e["nama_evaluasi"])
            for e in items[0].get("evaluasi_list", [])
        }

        for idx, student in enumerate(items, start=1):
            nisn = student.get("siswa_nisn", f"Baris #{idx}")

            # 1. Validasi Jam Belajar (Study Time)
            if student.get("studytime") is None:
                raise serializers.ValidationError(
                    f"Study Time untuk siswa (NISN: {nisn}) belum diisi. Pastikan seluruh field terisi."
                )

            eval_list = student.get("evaluasi_list", [])
            if not eval_list:
                raise serializers.ValidationError(
                    f"Daftar evaluasi untuk siswa (NISN: {nisn}) kosong."
                )

            # 2. Validasi Kelengkapan Kolom Evaluasi (misal: Quiz 1, Tugas, Quiz 2 harus seragam)
            student_eval_keys = {(e["jenis_evaluasi"], e["nama_evaluasi"]) for e in eval_list}
            if student_eval_keys != ref_eval_keys:
                raise serializers.ValidationError(
                    f"Komponen evaluasi untuk siswa (NISN: {nisn}) tidak lengkap atau terlewat. Pastikan semua kolom nilai terisi."
                )

            # 3. Validasi Skor Nilai Tidak Boleh Null
            for eval_item in eval_list:
                if eval_item.get("skor") is None:
                    raise serializers.ValidationError(
                        f"Nilai '{eval_item.get('nama_evaluasi')}' untuk siswa (NISN: {nisn}) belum diisi."
                    )

        return items


class PredictionResultInputSerializer(serializers.Serializer):
    siswa_nisn = serializers.CharField(max_length=20)
    mapel_id = serializers.IntegerField()
    semester_id = serializers.IntegerField()
    minggu_ke = serializers.IntegerField(min_value=1, max_value=16)
    risk_score = serializers.ChoiceField(choices=PredictionResult.RiskChoices.choices)
    recommendation = serializers.CharField()