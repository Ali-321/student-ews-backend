from typing import Dict, Any
from django.db.models import F, ExpressionWrapper, FloatField, Max, QuerySet, Avg, Count, Q, Subquery
from django.shortcuts import get_object_or_404

from academic.models import Siswa,Semester
from assessment.models import HistoriStudytime, NilaiSiswa, PresensiSiswa, PredictionResult
from django.db.models import Avg, Min, Case, When, Value, CharField, Q
from django.db.models.functions import Coalesce



def histori_studytime_list(*, filters: Dict[str, Any] = None) -> QuerySet[HistoriStudytime]:
    filters = filters or {}
    qs = HistoriStudytime.objects.select_related("siswa", "mapel", "semester").all()

    if "siswa_nisn" in filters:
        qs = qs.filter(siswa__nisn=filters["siswa_nisn"])
    if "mapel_id" in filters:
        qs = qs.filter(mapel_id=filters["mapel_id"])
    if "semester_id" in filters:
        qs = qs.filter(semester_id=filters["semester_id"])
    if "minggu_ke" in filters:
        qs = qs.filter(minggu_ke=filters["minggu_ke"])

    return qs


def nilai_siswa_list(*, filters: Dict[str, Any] = None) -> QuerySet[NilaiSiswa]:
    filters = filters or {}
    qs = NilaiSiswa.objects.select_related("siswa", "mapel", "semester").all()

    if "siswa_nisn" in filters:
        qs = qs.filter(siswa__nisn=filters["siswa_nisn"])
    if "mapel_id" in filters:
        qs = qs.filter(mapel_id=filters["mapel_id"])
    if "semester_id" in filters:
        qs = qs.filter(semester_id=filters["semester_id"])
    if "jenis_evaluasi" in filters:
        qs = qs.filter(jenis_evaluasi=filters["jenis_evaluasi"])
    if "minggu_ke" in filters:
        qs = qs.filter(minggu_ke=filters["minggu_ke"])

    return qs


def presensi_siswa_list(*, filters: Dict[str, Any] = None) -> QuerySet[PresensiSiswa]:
    filters = filters or {}
    qs = PresensiSiswa.objects.select_related("siswa", "mapel", "semester").all()

    if "siswa_nisn" in filters:
        qs = qs.filter(siswa__nisn=filters["siswa_nisn"])
    if "mapel_id" in filters:
        qs = qs.filter(mapel_id=filters["mapel_id"])
    if "semester_id" in filters:
        qs = qs.filter(semester_id=filters["semester_id"])
    if "status" in filters:
        qs = qs.filter(status=filters["status"])
    if "minggu_ke" in filters:
        qs = qs.filter(minggu_ke=filters["minggu_ke"])

    return qs


def prediction_result_list(*, filters: Dict[str, Any] = None) -> QuerySet[PredictionResult]:
    filters = filters or {}
    qs = PredictionResult.objects.select_related("siswa", "mapel", "semester").all()

    if "siswa_nisn" in filters:
        qs = qs.filter(siswa__nisn=filters["siswa_nisn"])
    if "mapel_id" in filters:
        qs = qs.filter(mapel_id=filters["mapel_id"])
    if "semester_id" in filters:
        qs = qs.filter(semester_id=filters["semester_id"])
    if "risk_score" in filters:
        qs = qs.filter(risk_score=filters["risk_score"])
    if "minggu_ke" in filters:
        qs = qs.filter(minggu_ke=filters["minggu_ke"])

    return qs


def get_ringkasan_akademik_siswa(*, siswa_nisn: str, semester_id: int) -> Dict[str, Any]:
    """
    Menghitung agregasi nilai, kehadiran, dan risiko EWS siswa dalam 1 semester.
    """
    nilai_qs = NilaiSiswa.objects.filter(siswa__nisn=siswa_nisn, semester_id=semester_id)
    presensi_qs = PresensiSiswa.objects.filter(siswa__nisn=siswa_nisn, semester_id=semester_id)
    prediction_qs = PredictionResult.objects.filter(siswa__nisn=siswa_nisn, semester_id=semester_id)
    latest_ids = (
        PredictionResult.objects.filter(
            siswa__nisn=siswa_nisn,
            semester_id=semester_id
        )
        .values("mapel_id")
        .annotate(max_id=Max("id"))
        .values("max_id")
    )

    avg_nilai = nilai_qs.aggregate(rata_rata=Avg("skor"))["rata_rata"] or 0.0

    presensi_stats = presensi_qs.aggregate(
        total=Count("id"),
        hadir=Count("id", filter=Q(status=PresensiSiswa.StatusChoices.HADIR)),
        alpa=Count("id", filter=Q(status=PresensiSiswa.StatusChoices.ALPA)),
        izin=Count("id", filter=Q(status=PresensiSiswa.StatusChoices.IZIN)),
        sakit=Count("id", filter=Q(status=PresensiSiswa.StatusChoices.SAKIT)),
    )

    total_presensi = presensi_stats["total"]
    persentase_kehadiran = (presensi_stats["hadir"] / total_presensi * 100) if total_presensi > 0 else 0.0

    latest_predictions = PredictionResult.objects.filter(id__in=Subquery(latest_ids))
    high_risk_count = sum(1 for p in latest_predictions if p.risk_score == PredictionResult.RiskChoices.HIGH)

    return {
        "siswa_nisn": siswa_nisn,
        "semester_id": semester_id,
        "rata_rata_nilai": round(avg_nilai, 2),
        "persentase_kehadiran": round(persentase_kehadiran, 2),
        "presensi_detail": presensi_stats,
        "total_mapel_berisiko_tinggi": high_risk_count,
    }

def get_presensi_status_choices():
    return [
        {"value": choice.value, "label": choice.label}
        for choice in PresensiSiswa.StatusChoices
    ]

def get_siswa_with_hybrid_risk_selector(
    *,
    semester_id: int = None,
    kelas_id: int = None,
    search: str = None,
    risk_status: str = None,
):
    queryset = Siswa.objects.select_related("kelas")

    # Jika semester_id tidak diberikan, ambil ID semester yang sedang aktif
    if semester_id is None:
        active_semester = Semester.objects.filter(is_aktif=True).first()
        if active_semester:
            semester_id = active_semester.id
            
    # 1. Filter dasar Master Data
    if kelas_id:
        queryset = queryset.filter(kelas_id=kelas_id)

    if search:
        queryset = queryset.filter(
            Q(nama__icontains=search) | Q(nisn__icontains=search)
        )

    # 2. Condition filter semester
    nilai_filter = Q(nilai_list__semester_id=semester_id) if semester_id else Q()
    pred_filter = Q(predictions__semester_id=semester_id) if semester_id else Q()
    pres_filter = Q(presensi_list__semester_id=semester_id) if semester_id else Q()

    # 3. Agregasi data
    queryset = queryset.annotate(
        avg_predicted_score=Coalesce(
            Avg("nilai_list__skor", filter=nilai_filter),
            0.0,
            output_field=FloatField(),
        ),
        max_risk_score=Coalesce(
            Max("predictions__risk_score", filter=pred_filter),
            0,
        ),
        total_presensi=Count("presensi_list", filter=pres_filter),
        total_hadir=Count(
            "presensi_list",
            filter=pres_filter & Q(presensi_list__status=PresensiSiswa.StatusChoices.HADIR),
        ),
    ).annotate(
        avg_presensi=Case(
            When(
                total_presensi__gt=0,
                then=ExpressionWrapper(
                    (F("total_hadir") * 100.0) / F("total_presensi"),
                    output_field=FloatField(),
                ),
            ),
            default=Value(0.0),
            output_field=FloatField(),
        ),
        risk_status=Case(
            When(max_risk_score=PredictionResult.RiskChoices.HIGH, then=Value("HIGH")),
            When(
                Q(max_risk_score=PredictionResult.RiskChoices.MEDIUM)
                | Q(avg_predicted_score__lt=80.0),
                then=Value("MEDIUM"),
            ),
            default=Value("LOW"),
            output_field=CharField(),
        ),
    )

    # 4. Filter berdasarkan status risiko yang dihitung
    if risk_status:
        queryset = queryset.filter(risk_status__iexact=risk_status)

    return queryset.order_by("nama")