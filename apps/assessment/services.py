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
def create_nilai_siswa(
    *,
    siswa_nisn: str,
    mapel_id: int,
    semester_id: int,
    minggu_ke: int,
    jenis_evaluasi: str,
    nama_evaluasi: str,
    skor: float,
    is_terlambat: bool = False
) -> NilaiSiswa:
    if not (0.0 <= skor <= 100.0):
        raise ValidationError({"skor": "Skor nilai harus berada dalam rentang 0.0 sampai 100.0"})

    siswa = Siswa.objects.get(nisn=siswa_nisn)
    mapel = MataPelajaran.objects.get(pk=mapel_id)
    semester = Semester.objects.get(pk=semester_id)

    return NilaiSiswa.objects.create(
        siswa=siswa,
        mapel=mapel,
        semester=semester,
        minggu_ke=minggu_ke,
        jenis_evaluasi=jenis_evaluasi,
        nama_evaluasi=nama_evaluasi,
        skor=skor,
        is_terlambat=is_terlambat
    )


@transaction.atomic
def bulk_record_presensi(
    *,
    mapel_id: int,
    semester_id: int,
    minggu_ke: int,
    tanggal: date,
    items: List[Dict[str, Any]]
) -> List[PresensiSiswa]:
    """
    Format items: [{"siswa_nisn": "00123", "status": "Hadir"}, ...]
    """
    mapel = MataPelajaran.objects.get(pk=mapel_id)
    semester = Semester.objects.get(pk=semester_id)

    records = []
    for item in items:
        siswa = Siswa.objects.get(nisn=item["siswa_nisn"])
        obj, _ = PresensiSiswa.objects.update_or_create(
            siswa=siswa,
            mapel=mapel,
            semester=semester,
            tanggal=tanggal,
            defaults={
                "minggu_ke": minggu_ke,
                "status": item["status"]
            }
        )
        records.append(obj)
    return records


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