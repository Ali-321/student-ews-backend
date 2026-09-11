from datetime import date
from typing import List, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError

from academic.models import Siswa, MataPelajaran, Semester
from assessment.models import HistoriStudytime, NilaiSiswa, PresensiSiswa, PredictionResult


@transaction.atomic
def record_studytime(
    *,
    siswa_nisn: str,
    mapel_id: int,
    semester_id: int,
    minggu_ke: int,
    studytime: int
) -> HistoriStudytime:
    siswa = Siswa.objects.get(nisn=siswa_nisn)
    mapel = MataPelajaran.objects.get(pk=mapel_id)
    semester = Semester.objects.get(pk=semester_id)

    obj, created = HistoriStudytime.objects.update_or_create(
        siswa=siswa,
        mapel=mapel,
        semester=semester,
        minggu_ke=minggu_ke,
        defaults={"studytime": studytime}
    )
    return obj

@transaction.atomic
def bulk_record_presensi(*, mapel_id: int, semester_id: int, tanggal_mulai, tanggal_akhir, items: list) -> list[PresensiSiswa]:
    semester = Semester.objects.get(id=semester_id)
    mapel = MataPelajaran.objects.get(id=mapel_id)

    presensi_records = []
    for student_item in items:
        siswa = Siswa.objects.get(nisn=student_item["siswa_nisn"])
        
        for harian in student_item["presensi_harian"]:
            tgl = harian["tanggal"]
            minggu_ke = semester.get_minggu_ke(target_date=tgl)

            presensi, _ = PresensiSiswa.objects.update_or_create(
                siswa=siswa,
                mapel=mapel,
                semester=semester,
                tanggal=tgl,
                defaults={
                    "minggu_ke": minggu_ke,
                    "status": harian["status"],
                }
            )
            presensi_records.append(presensi)

    return presensi_records


@transaction.atomic
def bulk_record_assessment(*, mapel_id: int, semester_id: int, tanggal_input, items: list) -> dict:
    semester = Semester.objects.get(id=semester_id)
    mapel = MataPelajaran.objects.get(id=mapel_id)
    
    # Hitung minggu_ke otomatis dari tanggal_input
    calculated_minggu_ke = semester.get_minggu_ke(target_date=tanggal_input)

    nilai_records = []
    studytime_records = []

    for student_item in items:
        siswa = Siswa.objects.get(nisn=student_item["siswa_nisn"])

        # 1. Upsert Study Time jika diisi
        if student_item.get("studytime") is not None:
            st, _ = HistoriStudytime.objects.update_or_create(
                siswa=siswa,
                mapel=mapel,
                semester=semester,
                minggu_ke=calculated_minggu_ke,
                defaults={"studytime": student_item["studytime"]}
            )
            studytime_records.append(st)

        # 2. Upsert Nilai Evaluasi (Quiz 1, Tugas, Quiz 2, dll)
        for eval_item in student_item.get("evaluasi_list", []):
            if eval_item.get("skor") is not None:
                nilai, _ = NilaiSiswa.objects.update_or_create(
                    siswa=siswa,
                    mapel=mapel,
                    semester=semester,
                    jenis_evaluasi=eval_item["jenis_evaluasi"],
                    nama_evaluasi=eval_item["nama_evaluasi"],
                    defaults={
                        "minggu_ke": calculated_minggu_ke,
                        "skor": eval_item["skor"],
                    }
                )
                nilai_records.append(nilai)

    return {
        "studytime_records": studytime_records,
        "nilai_records": nilai_records,
    }


@transaction.atomic
def record_prediction_result(
    *,
    siswa_nisn: str,
    mapel_id: int,
    semester_id: int,
    minggu_ke: int,
    risk_score: int,
    recommendation: str
) -> PredictionResult:
    siswa = Siswa.objects.get(nisn=siswa_nisn)
    mapel = MataPelajaran.objects.get(pk=mapel_id)
    semester = Semester.objects.get(pk=semester_id)

    obj, created = PredictionResult.objects.update_or_create(
        siswa=siswa,
        mapel=mapel,
        semester=semester,
        minggu_ke=minggu_ke,
        defaults={
            "risk_score": risk_score,
            "recommendation": recommendation
        }
    )
    return obj