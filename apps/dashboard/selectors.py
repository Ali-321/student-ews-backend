from django.db.models import Avg, Count, Max, Q

from academic.models import Kelas, MataPelajaran, Siswa
from assessment.models import NilaiSiswa, PredictionResult, PresensiSiswa


def get_dashboard_summary() -> dict:
  """Mengambil dan mengagregasi data ringkasan untuk DashboardSummaryView."""
  siswa_qs = Siswa.objects.all()
  total_siswa = siswa_qs.count()

  latest_week = (
      PredictionResult.objects.aggregate(max_w=Max('minggu_ke'))['max_w'] or 1
  )

  latest_preds = PredictionResult.objects.filter(
      siswa__in=siswa_qs, minggu_ke=latest_week
  )

  high_count = latest_preds.filter(
      risk_score=PredictionResult.RiskChoices.HIGH
  ).count()
  med_count = latest_preds.filter(
      risk_score=PredictionResult.RiskChoices.MEDIUM
  ).count()
  low_count = latest_preds.filter(
      risk_score=PredictionResult.RiskChoices.LOW
  ).count()

  total_preds = high_count + med_count + low_count or 1

  presensi_qs = PresensiSiswa.objects.filter(siswa__in=siswa_qs)
  total_presensi = presensi_qs.count()
  hadir_presensi = presensi_qs.filter(
      status=PresensiSiswa.StatusChoices.HADIR
  ).count()
  avg_presensi_global = (
      round((hadir_presensi / total_presensi * 100), 2)
      if total_presensi > 0
      else 0.0
  )

  nilai_qs = NilaiSiswa.objects.filter(siswa__in=siswa_qs)
  trend_performa = []

  for w in range(1, latest_week + 1):
    avg_n = (
        nilai_qs.filter(minggu_ke=w).aggregate(avg=Avg('skor'))['avg'] or 0.0
    )

    p_w = presensi_qs.filter(minggu_ke=w)
    p_total = p_w.count()
    p_hadir = p_w.filter(status=PresensiSiswa.StatusChoices.HADIR).count()
    avg_p = (p_hadir / p_total * 100) if p_total > 0 else 0.0

    trend_performa.append({
        'minggu_ke': w,
        'label': f'Minggu {w}',
        'rata_rata_nilai': round(avg_n, 1),
        'rata_rata_presensi': round(avg_p, 1),
    })

  proporsi_risiko = {
      'rendah': {
          'count': low_count,
          'percentage': round((low_count / total_preds) * 100, 1),
      },
      'sedang': {
          'count': med_count,
          'percentage': round((med_count / total_preds) * 100, 1),
      },
      'tinggi': {
          'count': high_count,
          'percentage': round((high_count / total_preds) * 100, 1),
      },
  }

  # Insight Kelas
  high_risk_preds_all = latest_preds.filter(
      risk_score=PredictionResult.RiskChoices.HIGH
  )
  high_risk_terbanyak_raw = (
      high_risk_preds_all.values('siswa__kelas__nama_kelas')
      .annotate(jumlah_siswa=Count('id'))
      .order_by('-jumlah_siswa')[:5]
  )
  high_risk_terbanyak = [
      {
          'nama_kelas': item['siswa__kelas__nama_kelas'] or 'Tanpa Kelas',
          'jumlah_siswa': item['jumlah_siswa'],
      }
      for item in high_risk_terbanyak_raw
  ]

  low_risk_preds_all = latest_preds.filter(
      risk_score=PredictionResult.RiskChoices.LOW
  )
  low_risk_terbanyak_raw = (
      low_risk_terbanyak_raw.values('siswa__kelas__nama_kelas')
      .annotate(jumlah_siswa=Count('id'))
      .order_by('-jumlah_siswa')[:5]
  ) if False else (
      low_risk_preds_all.values('siswa__kelas__nama_kelas')
      .annotate(jumlah_siswa=Count('id'))
      .order_by('-jumlah_siswa')[:5]
  )
  low_risk_terbanyak = [
      {
          'nama_kelas': item['siswa__kelas__nama_kelas'] or 'Tanpa Kelas',
          'jumlah_siswa': item['jumlah_siswa'],
      }
      for item in low_risk_terbanyak_raw
  ]

  insight_kelas = {
      'high_risk_terbanyak': high_risk_terbanyak,
      'low_risk_terbanyak': low_risk_terbanyak,
  }

  # Top Intervensi
  high_risk_preds_limit = high_risk_preds_all.select_related(
      'siswa', 'siswa__kelas'
  )[:5]

  top_intervensi = []
  for pred in high_risk_preds_limit:
    s = pred.siswa
    s_nilai = (
        nilai_qs.filter(siswa=s).aggregate(avg=Avg('skor'))['avg'] or 0.0
    )

    s_p_total = presensi_qs.filter(siswa=s).count()
    s_p_hadir = presensi_qs.filter(
        siswa=s, status=PresensiSiswa.StatusChoices.HADIR
    ).count()
    s_kehadiran = (s_p_hadir / s_p_total * 100) if s_p_total > 0 else 0.0

    top_intervensi.append({
        'nisn': s.nisn,
        'nama': s.nama,
        'kelas': s.kelas.nama_kelas if s.kelas else '-',
        'nilai': round(s_nilai, 1),
        'kehadiran': round(s_kehadiran, 1),
        'status_risk': 'HIGH',
    })

  return {
      'summary': {
          'total_siswa': total_siswa,
          'risiko_tinggi': high_count,
          'risiko_sedang': med_count,
          'rata_rata_presensi': avg_presensi_global,
      },
      'trend_performa': trend_performa,
      'proporsi_risiko': proporsi_risiko,
      'insight_kelas': insight_kelas,
      'top_intervensi': top_intervensi,
  }


def get_school_analytics(
    kelas_id: int | None = None, mapel_id: int | None = None
) -> dict:
  """Mengambil dan mengagregasi statistik analisis sekolah untuk DashboardAnalyticsView."""
  kelas_options = list(Kelas.objects.values('id', 'nama_kelas'))
  mapel_options = list(MataPelajaran.objects.values('id', 'nama_mapel'))
  filter_options = {'kelas': kelas_options, 'mapel': mapel_options}

  siswa_qs = Siswa.objects.all()
  if kelas_id:
    siswa_qs = siswa_qs.filter(kelas_id=kelas_id)

  latest_week = (
      PredictionResult.objects.aggregate(max_w=Max('minggu_ke'))['max_w'] or 1
  )

  pred_qs = PredictionResult.objects.filter(
      siswa__in=siswa_qs, minggu_ke=latest_week
  )
  if mapel_id:
    pred_qs = pred_qs.filter(mapel_id=mapel_id)

  high_risk_preds = pred_qs.filter(
      risk_score=PredictionResult.RiskChoices.HIGH
  )

  perbandingan_kelas_raw = (
      high_risk_preds.values('siswa__kelas__nama_kelas')
      .annotate(jumlah_high_risk=Count('id'))
      .order_by('siswa__kelas__nama_kelas')
  )

  perbandingan_risiko_kelas = [
      {
          'nama_kelas': item['siswa__kelas__nama_kelas'] or 'Tanpa Kelas',
          'jumlah_high_risk': item['jumlah_high_risk'],
      }
      for item in perbandingan_kelas_raw
  ]

  high_risk_tuples = set(high_risk_preds.values_list('siswa_id', 'mapel_id'))
  total_high_risk_cases = len(high_risk_preds) or 1
  high_risk_siswa_ids = [s_id for s_id, _ in high_risk_tuples]

  # 1. Presensi Rendah
  presensi_qs = PresensiSiswa.objects.filter(siswa_id__in=high_risk_siswa_ids)
  if mapel_id:
    presensi_qs = presensi_qs.filter(mapel_id=mapel_id)

  presensi_stats = presensi_qs.values('siswa_id', 'mapel_id').annotate(
      total=Count('id'),
      hadir=Count(
          'id',
          filter=Q(status=PresensiSiswa.StatusChoices.HADIR),
      ),
  )

  low_attendance_count = sum(
      1
      for p in presensi_stats
      if (p['siswa_id'], p['mapel_id']) in high_risk_tuples
      and p['total'] > 0
      and ((p['hadir'] / p['total']) * 100) < 75.0
  )

  # 2. Nilai Ujian
  nilai_qs = NilaiSiswa.objects.filter(siswa_id__in=high_risk_siswa_ids)
  if mapel_id:
    nilai_qs = nilai_qs.filter(mapel_id=mapel_id)

  exam_choices = [
      NilaiSiswa.EvaluasiChoices.QUIZ,
      NilaiSiswa.EvaluasiChoices.QUIZ2,
      NilaiSiswa.EvaluasiChoices.UTS,
      NilaiSiswa.EvaluasiChoices.UAS,
  ]

  exam_stats = (
      nilai_qs.filter(jenis_evaluasi__in=exam_choices)
      .values('siswa_id', 'mapel_id')
      .annotate(avg_exam=Avg('skor'))
  )

  low_exam_count = sum(
      1
      for e in exam_stats
      if (e['siswa_id'], e['mapel_id']) in high_risk_tuples
      and (e['avg_exam'] or 0) < 70.0
  )

  # 3. Nilai Tugas
  assignment_stats = (
      nilai_qs.filter(jenis_evaluasi=NilaiSiswa.EvaluasiChoices.TUGAS)
      .values('siswa_id', 'mapel_id')
      .annotate(avg_assignment=Avg('skor'))
  )

  low_assignment_count = sum(
      1
      for a in assignment_stats
      if (a['siswa_id'], a['mapel_id']) in high_risk_tuples
      and (a['avg_assignment'] or 0) < 70.0
  )

  faktor_utama_risiko = [
      {
          'faktor': 'Presensi Rendah (<75%)',
          'count': low_attendance_count,
          'percentage': round(
              (low_attendance_count / total_high_risk_cases) * 100, 1
          ),
      },
      {
          'faktor': 'Nilai Ujian < KKM',
          'count': low_exam_count,
          'percentage': round(
              (low_exam_count / total_high_risk_cases) * 100, 1
          ),
      },
      {
          'faktor': 'Nilai Tugas Rendah',
          'count': low_assignment_count,
          'percentage': round(
              (low_assignment_count / total_high_risk_cases) * 100, 1
          ),
      },
  ]

  return {
      'filter_options': filter_options,
      'perbandingan_risiko_kelas': perbandingan_risiko_kelas,
      'faktor_utama_risiko': faktor_utama_risiko,
  }