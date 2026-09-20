from typing import Dict, Any
from django.db.models import  Max, QuerySet, Avg, Count, Q, Subquery, Sum
from django.shortcuts import get_object_or_404

from academic.models import MataPelajaran, Siswa
from assessment.models import HistoriStudytime, NilaiSiswa, PresensiSiswa, PredictionResult
from django.db.models import Avg, Q




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
    nilai_qs = NilaiSiswa.objects.filter(siswa__nisn=siswa_nisn, semester_id=semester_id)
    presensi_qs = PresensiSiswa.objects.filter(siswa__nisn=siswa_nisn, semester_id=semester_id)
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



def get_siswa_risk_summary_qs(
    kelas_id: int = None,
    search: str = None,
    risk_status: str = None,
) -> QuerySet[Siswa]:
    """Mengambil QuerySet dasar siswa dengan filter relasional yang super cepat."""
    qs = Siswa.objects.select_related('kelas').all().order_by('nama')

    if kelas_id:
        qs = qs.filter(kelas_id=kelas_id)
        
    if search:
        qs = qs.filter(Q(nama__icontains=search) | Q(nisn__icontains=search))

    if risk_status:
        latest_week = PredictionResult.objects.aggregate(max_w=Max('minggu_ke'))['max_w']
        if latest_week:
            latest_preds = PredictionResult.objects.filter(minggu_ke=latest_week).values('siswa__nisn', 'risk_score')
            risk_map = {}
            for p in latest_preds:
                sid = p['siswa__nisn']
                raw_score = p['risk_score']
                
                # PERBAIKAN: Konversi Enum/Integer ke String secara eksplisit
                if raw_score == PredictionResult.RiskChoices.HIGH:
                    score_str = "HIGH"
                elif raw_score == PredictionResult.RiskChoices.MEDIUM:
                    score_str = "MEDIUM"
                else:
                    score_str = "LOW"

                if sid not in risk_map:
                    risk_map[sid] = score_str
                else:
                    # Logika hierarki berdasar string
                    if score_str == "HIGH":
                        risk_map[sid] = "HIGH"
                    elif score_str == "MEDIUM" and risk_map[sid] != "HIGH":
                        risk_map[sid] = "MEDIUM"
            
            matched_siswa_nisns = [sid for sid, status in risk_map.items() if status == risk_status.upper()]
            qs = qs.filter(nisn__in=matched_siswa_nisns)
        else:
            qs = qs.none()

    return qs


def attach_metrics_to_paginated_siswa(siswa_list):
    """Menghitung metrik EWS HANYA untuk sekumpulan siswa pasca-paginasi."""
    siswa_nisns = [s.nisn for s in siswa_list]
    if not siswa_nisns:
        return siswa_list

    nilai_aggs = NilaiSiswa.objects.filter(siswa__nisn__in=siswa_nisns).values('siswa__nisn').annotate(
        avg_nilai=Avg('skor')
    )
    nilai_map = {item['siswa__nisn']: round(item['avg_nilai'], 1) if item['avg_nilai'] else 0.0 for item in nilai_aggs}

    presensi_aggs = PresensiSiswa.objects.filter(siswa__nisn__in=siswa_nisns).values('siswa__nisn').annotate(
        total=Count('id'),
        hadir=Count('id', filter=Q(status=PresensiSiswa.StatusChoices.HADIR))
    )
    presensi_map = {}
    for p in presensi_aggs:
        pct = (p['hadir'] / p['total'] * 100) if p['total'] > 0 else 0.0
        presensi_map[p['siswa__nisn']] = f"{round(pct, 1)}%"

    latest_week = PredictionResult.objects.aggregate(max_w=Max('minggu_ke'))['max_w']
    risk_map = {}
    if latest_week:
        preds = PredictionResult.objects.filter(siswa__nisn__in=siswa_nisns, minggu_ke=latest_week).values('siswa__nisn', 'risk_score')
        for p in preds:
            sid = p['siswa__nisn']
            raw_score = p['risk_score']
            
            # PERBAIKAN: Konversi Enum/Integer ke String secara eksplisit
            if raw_score == PredictionResult.RiskChoices.HIGH:
                score_str = "HIGH"
            elif raw_score == PredictionResult.RiskChoices.MEDIUM:
                score_str = "MEDIUM"
            else:
                score_str = "LOW"

            if sid not in risk_map:
                risk_map[sid] = score_str
            else:
                # Logika hierarki berdasar string
                if score_str == "HIGH":
                    risk_map[sid] = "HIGH"
                elif score_str == "MEDIUM" and risk_map[sid] != "HIGH":
                    risk_map[sid] = "MEDIUM"

    for siswa in siswa_list:
        siswa.calc_nilai = nilai_map.get(siswa.nisn, 0.0)
        siswa.calc_presensi = presensi_map.get(siswa.nisn, "0%")
        siswa.calc_risk = risk_map.get(siswa.nisn, "LOW")

    return siswa_list
def get_siswa_risk_detail(nisn: str, mapel_id: int | None = None) -> dict:
    # 1. Profil Siswa
    siswa = get_object_or_404(Siswa.objects.select_related('kelas'), nisn=nisn)
    
    profil_siswa = {
        "nisn": siswa.nisn,
        "nama_siswa": siswa.nama,
        "kelas": siswa.kelas.nama_kelas if siswa.kelas else "-",
        "gender": getattr(siswa, 'gender', '-')
    }

    # 2. Logika Auto-Default Mapel (Mencegah Distorsi Data)
    mapel_qs = MataPelajaran.objects.all().order_by('id')
    if not mapel_qs.exists():
        raise ValueError("Belum ada data Mata Pelajaran di sistem.")

    if mapel_id:
        mapel_aktif = get_object_or_404(mapel_qs, id=mapel_id)
    else:
        mapel_aktif = mapel_qs.first()

    mapel_data = {
        "id": mapel_aktif.id,
        "nama_mapel": mapel_aktif.nama_mapel
    }

    # 3. Tentukan Minggu Terbaru (Spesifik untuk Mapel yang Dipilih)
    latest_week = PredictionResult.objects.filter(
        siswa=siswa, mapel=mapel_aktif
    ).aggregate(max_w=Max('minggu_ke'))['max_w']
    
    if not latest_week:
        latest_week = 1 

    # 4. Filter Kueri Murni untuk 1 Siswa, 1 Mapel, 1 Minggu
    nilai_qs = NilaiSiswa.objects.filter(siswa=siswa, mapel=mapel_aktif, minggu_ke=latest_week)
    presensi_qs = PresensiSiswa.objects.filter(siswa=siswa, mapel=mapel_aktif, minggu_ke=latest_week)
    studytime_qs = HistoriStudytime.objects.filter(siswa=siswa, mapel=mapel_aktif, minggu_ke=latest_week)

    # 5. Metrik Kinerja Aktual Formatif (Minggu Terakhir)
    total_absen = presensi_qs.count()
    total_hadir = presensi_qs.filter(status=PresensiSiswa.StatusChoices.HADIR).count()
    kehadiran_pct = (total_hadir / total_absen * 100) if total_absen > 0 else 0.0

    skor_tugas = nilai_qs.filter(jenis_evaluasi=NilaiSiswa.EvaluasiChoices.TUGAS).aggregate(avg=Avg('skor'))['avg'] or 0.0
    skor_quiz1 = nilai_qs.filter(jenis_evaluasi=NilaiSiswa.EvaluasiChoices.QUIZ).aggregate(avg=Avg('skor'))['avg'] or 0.0
    skor_quiz2 = nilai_qs.filter(jenis_evaluasi=NilaiSiswa.EvaluasiChoices.QUIZ2).aggregate(avg=Avg('skor'))['avg'] or 0.0
    
    # Study hour dijumlahkan (Sum), bukan dirata-rata
    total_study = studytime_qs.aggregate(total=Sum('studytime'))['total'] or 0.0

    metrik_kinerja = {
        "kehadiran_pct": round(kehadiran_pct, 1),
        "study_hour": round(total_study, 1),
        "rata_rata_tugas": round(skor_tugas, 1),
        "rata_rata_pretest": round(skor_quiz1, 1),
        "rata_rata_posttest": round(skor_quiz2, 1),
    }

    # 6. Analisis EWS
    status_risiko = "LOW"
    tingkat_risiko_display = "Rendah"
    rekomendasi_tindakan = "Belum ada data evaluasi atau prediksi untuk siswa ini."

    preds = PredictionResult.objects.filter(siswa=siswa, mapel=mapel_aktif, minggu_ke=latest_week)

    if preds.exists():
        target_pred = preds.first()
        score_enum = target_pred.risk_score
        
        if score_enum == PredictionResult.RiskChoices.HIGH:
            status_risiko = "HIGH"
            tingkat_risiko_display = "Tinggi"
        elif score_enum == PredictionResult.RiskChoices.MEDIUM:
            status_risiko = "MEDIUM"
            tingkat_risiko_display = "Sedang"
        else:
            status_risiko = "LOW"
            tingkat_risiko_display = "Rendah"

        rec_json = target_pred.recommendation
        if isinstance(rec_json, dict) and "guru" in rec_json:
            rekomendasi_tindakan = rec_json["guru"]
        else:
            rekomendasi_tindakan = "Lakukan pemantauan rutin terhadap performa siswa."

    analisis_ews = {
        "status_risiko": status_risiko,
        "tingkat_risiko_display": tingkat_risiko_display,
        "rekomendasi_tindakan": rekomendasi_tindakan
    }

    return {
        "profil_siswa": profil_siswa,
        "mapel_aktif": mapel_data, 
        "metrik_kinerja": metrik_kinerja,
        "analisis_ews": analisis_ews
    }