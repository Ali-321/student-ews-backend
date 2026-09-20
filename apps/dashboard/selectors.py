from django.db.models import Avg, Count, Max, Q
from django.shortcuts import get_object_or_404
from academic.models import Kelas, MataPelajaran, Siswa
from assessment.models import NilaiSiswa, PredictionResult, PresensiSiswa, HistoriStudytime
from django.db.models import Sum
from academic.models import Semester


def get_dashboard_summary(
    kelas_id: int | None = None, mapel_id: int | None = None
) -> dict:
    """Mengambil dan mengagregasi data ringkasan untuk DashboardSummaryView."""
    
    # 1. Base Query Filter
    siswa_qs = Siswa.objects.all()
    if kelas_id:
        siswa_qs = siswa_qs.filter(kelas_id=kelas_id)

    total_siswa = siswa_qs.count()
    latest_week = PredictionResult.objects.aggregate(max_w=Max('minggu_ke'))['max_w'] or 1

    # 2. Pemetaan Risiko Global (Hierarki: 1 High = Semua High)
    pred_qs = PredictionResult.objects.filter(siswa__in=siswa_qs, minggu_ke=latest_week)
    if mapel_id:
        pred_qs = pred_qs.filter(mapel_id=mapel_id)
        
    preds_values = pred_qs.values('siswa__nisn', 'risk_score', 'siswa__kelas__nama_kelas')
    
    siswa_kelas_map = {}
    risk_map = {}
    
    for p in preds_values:
        nisn = p['siswa__nisn']
        raw_score = p['risk_score']
        kelas_nama = p['siswa__kelas__nama_kelas'] or 'Tanpa Kelas'
        
        siswa_kelas_map[nisn] = kelas_nama
        
        if raw_score == PredictionResult.RiskChoices.HIGH:
            score_str = "HIGH"
        elif raw_score == PredictionResult.RiskChoices.MEDIUM:
            score_str = "MEDIUM"
        else:
            score_str = "LOW"
            
        if nisn not in risk_map:
            risk_map[nisn] = score_str
        else:
            if score_str == "HIGH":
                risk_map[nisn] = "HIGH"
            elif score_str == "MEDIUM" and risk_map[nisn] != "HIGH":
                risk_map[nisn] = "MEDIUM"

    high_count = list(risk_map.values()).count("HIGH")
    med_count = list(risk_map.values()).count("MEDIUM")
    low_count = list(risk_map.values()).count("LOW")
    total_preds = len(risk_map) or 1

    # 3. Filter Presensi Global
    presensi_qs = PresensiSiswa.objects.filter(siswa__in=siswa_qs)
    if mapel_id:
        presensi_qs = presensi_qs.filter(mapel_id=mapel_id)
        
    total_presensi = presensi_qs.count()
    hadir_presensi = presensi_qs.filter(status=PresensiSiswa.StatusChoices.HADIR).count()
    avg_presensi_global = round((hadir_presensi / total_presensi * 100), 2) if total_presensi > 0 else 0.0

    # 4. Filter Nilai Global & Tren Performa
    nilai_qs = NilaiSiswa.objects.filter(siswa__in=siswa_qs)
    if mapel_id:
        nilai_qs = nilai_qs.filter(mapel_id=mapel_id)
        
    trend_performa = []
    for w in range(1, latest_week + 1):
        avg_n = nilai_qs.filter(minggu_ke=w).aggregate(avg=Avg('skor'))['avg'] or 0.0
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
        'rendah': {'count': low_count, 'percentage': round((low_count / total_preds) * 100, 1)},
        'sedang': {'count': med_count, 'percentage': round((med_count / total_preds) * 100, 1)},
        'tinggi': {'count': high_count, 'percentage': round((high_count / total_preds) * 100, 1)},
    }

    # 5. Insight Kelas (Berdasarkan Risiko Global)
    class_risk_counts = {}
    for nisn, global_risk in risk_map.items():
        k_nama = siswa_kelas_map[nisn]
        if k_nama not in class_risk_counts:
            class_risk_counts[k_nama] = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        class_risk_counts[k_nama][global_risk] += 1

    high_risk_classes = sorted([{'nama_kelas': k, 'jumlah_siswa': v['HIGH']} for k, v in class_risk_counts.items()], key=lambda x: x['jumlah_siswa'], reverse=True)[:5]
    low_risk_classes = sorted([{'nama_kelas': k, 'jumlah_siswa': v['LOW']} for k, v in class_risk_counts.items()], key=lambda x: x['jumlah_siswa'], reverse=True)[:5]

    insight_kelas = {
        'high_risk_terbanyak': high_risk_classes,
        'low_risk_terbanyak': low_risk_classes,
    }

    # 6. Top Intervensi (Ambil NISN yang HIGH risk saja)
    high_risk_nisns = [nisn for nisn, risk in risk_map.items() if risk == "HIGH"]
    top_siswa_qs = Siswa.objects.filter(nisn__in=high_risk_nisns).select_related('kelas')[:5]
    
    top_intervensi = []
    for s in top_siswa_qs:
        s_nilai = nilai_qs.filter(siswa=s).aggregate(avg=Avg('skor'))['avg'] or 0.0
        s_p_total = presensi_qs.filter(siswa=s).count()
        s_p_hadir = presensi_qs.filter(siswa=s, status=PresensiSiswa.StatusChoices.HADIR).count()
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

    latest_week = PredictionResult.objects.aggregate(max_w=Max('minggu_ke'))['max_w'] or 1

    # 1. Pemetaan Risiko Global
    pred_qs = PredictionResult.objects.filter(siswa__in=siswa_qs, minggu_ke=latest_week)
    if mapel_id:
        pred_qs = pred_qs.filter(mapel_id=mapel_id)
        
    preds_values = pred_qs.values('siswa__nisn', 'risk_score', 'siswa__kelas__nama_kelas')
    
    siswa_kelas_map = {}
    risk_map = {}
    
    for p in preds_values:
        nisn = p['siswa__nisn']
        raw_score = p['risk_score']
        kelas_nama = p['siswa__kelas__nama_kelas'] or 'Tanpa Kelas'
        
        siswa_kelas_map[nisn] = kelas_nama
        
        if raw_score == PredictionResult.RiskChoices.HIGH:
            score_str = "HIGH"
        elif raw_score == PredictionResult.RiskChoices.MEDIUM:
            score_str = "MEDIUM"
        else:
            score_str = "LOW"
            
        if nisn not in risk_map:
            risk_map[nisn] = score_str
        else:
            if score_str == "HIGH":
                risk_map[nisn] = "HIGH"
            elif score_str == "MEDIUM" and risk_map[nisn] != "HIGH":
                risk_map[nisn] = "MEDIUM"
                
    class_risk_counts = {}
    for nisn, global_risk in risk_map.items():
        k_nama = siswa_kelas_map[nisn]
        if k_nama not in class_risk_counts:
            class_risk_counts[k_nama] = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        class_risk_counts[k_nama][global_risk] += 1

    perbandingan_risiko_kelas = [
        {
            'nama_kelas': k,
            'jumlah_high_risk': v['HIGH'],
            'jumlah_medium_risk': v['MEDIUM'],
            'jumlah_low_risk': v['LOW'],
        }
        for k, v in sorted(class_risk_counts.items())
    ]

   # 2. Investigasi Faktor Utama Risiko (Seluruh Siswa)
    total_siswa_cases = siswa_qs.count() or 1

    # Indikator 1: Presensi Rendah (< 75%)
    presensi_qs = PresensiSiswa.objects.filter(siswa__in=siswa_qs)
    if mapel_id: 
        presensi_qs = presensi_qs.filter(mapel_id=mapel_id)
    
    presensi_stats = presensi_qs.values('siswa__nisn').annotate(
        total=Count('id'),
        hadir=Count('id', filter=Q(status=PresensiSiswa.StatusChoices.HADIR)),
    )
    low_attendance_count = sum(1 for p in presensi_stats if p['total'] > 0 and ((p['hadir'] / p['total']) * 100) < 75.0)

    # Indikator 2: Study Hour Minim (< 2 Jam rata-rata)
    study_qs = HistoriStudytime.objects.filter(siswa__in=siswa_qs)
    if mapel_id: 
        study_qs = study_qs.filter(mapel_id=mapel_id)
    
    study_stats = study_qs.values('siswa__nisn').annotate(avg_study=Avg('studytime'))
    low_study_count = sum(1 for s in study_stats if (s['avg_study'] or 0) < 2.0)

    # Indikator 3-5: Kinerja Formatif (< KKM 70)
    nilai_qs = NilaiSiswa.objects.filter(siswa__in=siswa_qs)
    if mapel_id: 
        nilai_qs = nilai_qs.filter(mapel_id=mapel_id)

    def count_low_scores(eval_type, threshold=70.0):
        qs = nilai_qs.filter(jenis_evaluasi=eval_type).values('siswa__nisn').annotate(avg_skor=Avg('skor'))
        return sum(1 for q in qs if (q['avg_skor'] or 0) < threshold)

    low_quiz1_count = count_low_scores(NilaiSiswa.EvaluasiChoices.QUIZ)
    low_quiz2_count = count_low_scores(NilaiSiswa.EvaluasiChoices.QUIZ2)
    low_tugas_count = count_low_scores(NilaiSiswa.EvaluasiChoices.TUGAS)

    faktor_utama_risiko = [
        {
            'faktor': 'Presensi Minim (<75%)',
            'count': low_attendance_count,
            'percentage': round((low_attendance_count / total_siswa_cases) * 100, 1),
        },
        {
            'faktor': 'Waktu Belajar Rendah (<2 Jam)',
            'count': low_study_count,
            'percentage': round((low_study_count / total_siswa_cases) * 100, 1),
        },
        {
            'faktor': 'Pre-Test (Quiz 1) < KKM',
            'count': low_quiz1_count,
            'percentage': round((low_quiz1_count / total_siswa_cases) * 100, 1),
        },
        {
            'faktor': 'Post-Test (Quiz 2) < KKM',
            'count': low_quiz2_count,
            'percentage': round((low_quiz2_count / total_siswa_cases) * 100, 1),
        },
        {
            'faktor': 'Nilai Tugas Rendah',
            'count': low_tugas_count,
            'percentage': round((low_tugas_count / total_siswa_cases) * 100, 1),
        },
    ]

    return {
        'filter_options': filter_options,
        'perbandingan_risiko_kelas': perbandingan_risiko_kelas,
        'faktor_utama_risiko': faktor_utama_risiko,
    }


def get_dashboard_siswa_summary(*, siswa_nisn: str, mapel_id: int | None = None) -> dict:
    """Mengambil data dashboard spesifik 1 Siswa untuk 1 Mapel (di minggu terbaru)."""
    
    # 1. Ambil Profil Siswa
    siswa = get_object_or_404(Siswa.objects.select_related('kelas'), nisn=siswa_nisn)
    
    profil_data = {
        "nisn": siswa.nisn,
        "nama_siswa": siswa.nama,
        "kelas": siswa.kelas.nama_kelas if siswa.kelas else "-"
    }

    # 2. Logika Pemilihan Mapel (Default oleh Backend)
    mapel_qs = MataPelajaran.objects.all().order_by('id')
    if not mapel_qs.exists():
        raise ValueError("Belum ada data Mata Pelajaran di sistem.")

    if mapel_id:
        mapel_aktif = get_object_or_404(mapel_qs, id=mapel_id)
    else:
        mapel_aktif = mapel_qs.first()  # Default mutlak ke mapel pertama

    filter_opsi_mapel = list(mapel_qs.values('id', 'nama_mapel'))

    # 3. Identifikasi Minggu Terbaru secara Dinamis
    # Kita cari minggu_ke tertinggi yang pernah dicapai siswa ini di mapel terkait
    latest_pred = PredictionResult.objects.filter(siswa=siswa, mapel=mapel_aktif).aggregate(Max('minggu_ke'))['minggu_ke__max']
    latest_nilai = NilaiSiswa.objects.filter(siswa=siswa, mapel=mapel_aktif).aggregate(Max('minggu_ke'))['minggu_ke__max']
    latest_pres = PresensiSiswa.objects.filter(siswa=siswa, mapel=mapel_aktif).aggregate(Max('minggu_ke'))['minggu_ke__max']
    
    # Ambil nilai max dari ketiganya, jika kosong semua default ke 1
    minggu_terbaru = max(filter(None, [latest_pred, latest_nilai, latest_pres, 1]))

    # 4. Kalkulasi Study Time
    study_qs = HistoriStudytime.objects.filter(siswa=siswa, mapel=mapel_aktif, minggu_ke=minggu_terbaru)
    study_time = study_qs.aggregate(total=Avg('studytime'))['total'] or 0.0

    # 5. Agregasi Presensi (Dipetakan absolut ke Senin - Jumat)
    presensi_minggu_ini = PresensiSiswa.objects.filter(siswa=siswa, mapel=mapel_aktif, minggu_ke=minggu_terbaru)
    
    hari_map = {0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat"}
    presensi_data_mentah = {}
    
    # Tarik data dan petakan berdasarkan index hari (weekday)
    for p in presensi_minggu_ini:
        if p.tanggal:
            idx_hari = p.tanggal.weekday()
            if idx_hari <= 4:  # Hanya tampung Senin - Jumat
                presensi_data_mentah[idx_hari] = p.get_status_display()

    presensi_harian = []
    for i in range(5):
        presensi_harian.append({
            "hari": hari_map[i],
            "status": presensi_data_mentah.get(i, "-") # Jika tidak ada kelas di hari itu, output "-"
        })

    # 6. Agregasi Nilai Formatif (Sesuai UI)
    nilai_qs = NilaiSiswa.objects.filter(siswa=siswa, mapel=mapel_aktif, minggu_ke=minggu_terbaru)
    
    pretest = nilai_qs.filter(jenis_evaluasi=NilaiSiswa.EvaluasiChoices.QUIZ).aggregate(avg=Avg('skor'))['avg']
    posttest = nilai_qs.filter(jenis_evaluasi=NilaiSiswa.EvaluasiChoices.QUIZ2).aggregate(avg=Avg('skor'))['avg']
    assessment = nilai_qs.filter(jenis_evaluasi=NilaiSiswa.EvaluasiChoices.TUGAS).aggregate(avg=Avg('skor'))['avg']

    # 7. Analisis EWS
    pred_obj = PredictionResult.objects.filter(siswa=siswa, mapel=mapel_aktif, minggu_ke=minggu_terbaru).first()
    
    if pred_obj:
        status_risiko = pred_obj.get_risk_score_display().upper()
        label_risiko_display = f"Risiko {status_risiko.capitalize()}"
        
        # Ekstrak rekomendasi khusus siswa
        rekomendasi_mentah = pred_obj.recommendation
        rekomendasi_list = []
        if isinstance(rekomendasi_mentah, dict) and "siswa" in rekomendasi_mentah:
            rek_teks = rekomendasi_mentah["siswa"]
            # Memecah kalimat berdasarkan titik untuk dijadikan list array (bullet points)
            rekomendasi_list = [kalimat.strip() for kalimat in rek_teks.split('.') if kalimat.strip()]
        else:
            rekomendasi_list = [str(rekomendasi_mentah)]
    else:
        status_risiko = "LOW"
        label_risiko_display = "Risiko Rendah (Aman)"
        rekomendasi_list = ["Belum ada data evaluasi AI untuk minggu ini. Terus pertahankan belajarmu!"]

    # 8. Susun dan Return Sesuai Struktur JSON
    return {
        "profil": profil_data,
        "mapel_aktif": {
            "id": mapel_aktif.id,
            "nama_mapel": mapel_aktif.nama_mapel
        },
        "filter_opsi_mapel": filter_opsi_mapel,
        "ringkasan_mingguan": {
            "minggu_ke": minggu_terbaru,
            "study_time_jam": round(study_time, 1),
            "presensi_harian": presensi_harian,
            "nilai": {
                "tugas_1_pretest": round(pretest, 1) if pretest is not None else None,
                "tugas_2_posttest": round(posttest, 1) if posttest is not None else None,
                "assessment": round(assessment, 1) if assessment is not None else None
            }
        },
        "analisis_ews": {
            "status_risiko": status_risiko,
            "label_risiko_display": label_risiko_display,
            "rekomendasi": rekomendasi_list
        }
    }





def get_dashboard_ortu_summary(*, siswa_nisn: str, mapel_id: int | None = None) -> dict:
    """Mengambil data Time-Series untuk Dashboard Orang Tua dikunci pada Semester Aktif."""
    
    # 1. Ambil Profil Siswa & Semester Aktif
    siswa = get_object_or_404(Siswa.objects.select_related('kelas'), nisn=siswa_nisn)
    active_semester = Semester.objects.filter(is_aktif=True).first()
    
    profil_data = {
        "nisn": siswa.nisn,
        "nama_siswa": siswa.nama,
        "kelas": siswa.kelas.nama_kelas if siswa.kelas else "-"
    }

    if not active_semester:
        raise ValueError("Tidak ada semester aktif di sistem saat ini.")

    # 2. Logika Pemilihan Mapel (Default oleh Backend)
    mapel_qs = MataPelajaran.objects.all().order_by('id')
    if not mapel_qs.exists():
        raise ValueError("Belum ada data Mata Pelajaran di sistem.")

    if mapel_id:
        mapel_aktif = get_object_or_404(mapel_qs, id=mapel_id)
    else:
        mapel_aktif = mapel_qs.first()

    filter_opsi_mapel = list(mapel_qs.values('id', 'nama_mapel'))

    # 3. Cari Max Minggu Ke- pada SEMESTER AKTIF
    pred_w = PredictionResult.objects.filter(siswa=siswa, mapel=mapel_aktif, semester=active_semester).aggregate(Max('minggu_ke'))['minggu_ke__max']
    nilai_w = NilaiSiswa.objects.filter(siswa=siswa, mapel=mapel_aktif, semester=active_semester).aggregate(Max('minggu_ke'))['minggu_ke__max']
    pres_w = PresensiSiswa.objects.filter(siswa=siswa, mapel=mapel_aktif, semester=active_semester).aggregate(Max('minggu_ke'))['minggu_ke__max']
    
    minggu_terbaru = max(filter(None, [pred_w, nilai_w, pres_w, 1]))

    # 4. Bangun Dataset Grafik Mingguan & Tarik Data Mentah
    grafik_mingguan = []
    
    semua_nilai = NilaiSiswa.objects.filter(siswa=siswa, mapel=mapel_aktif, semester=active_semester)
    semua_presensi = PresensiSiswa.objects.filter(siswa=siswa, mapel=mapel_aktif, semester=active_semester)
    semua_study = HistoriStudytime.objects.filter(siswa=siswa, mapel=mapel_aktif, semester=active_semester)

    for w in range(1, minggu_terbaru + 1):
        p_minggu = semua_presensi.filter(minggu_ke=w)
        p_total = p_minggu.count()
        p_hadir = p_minggu.filter(status=PresensiSiswa.StatusChoices.HADIR).count()
        pct_presensi = (p_hadir / p_total * 100) if p_total > 0 else 0.0

        jam_belajar = semua_study.filter(minggu_ke=w).aggregate(total=Sum('studytime'))['total'] or 0.0

        n_minggu = semua_nilai.filter(minggu_ke=w)
        pretest = n_minggu.filter(jenis_evaluasi=NilaiSiswa.EvaluasiChoices.QUIZ).aggregate(avg=Avg('skor'))['avg']
        posttest = n_minggu.filter(jenis_evaluasi=NilaiSiswa.EvaluasiChoices.QUIZ2).aggregate(avg=Avg('skor'))['avg']
        assessment = n_minggu.filter(jenis_evaluasi=NilaiSiswa.EvaluasiChoices.TUGAS).aggregate(avg=Avg('skor'))['avg']

        grafik_mingguan.append({
            "minggu_ke": w,
            "label": f"Minggu {w}",
            "presensi_persen": round(pct_presensi, 1),
            "study_time_jam": round(jam_belajar, 1),
            "nilai": {
                "pretest": round(pretest, 1) if pretest is not None else None,
                "assessment": round(assessment, 1) if assessment is not None else None,
                "posttest": round(posttest, 1) if posttest is not None else None
            }
        })

    # 5. Logika Komparasi Bulanan (Metode Rolling Window 4-Mingguan)
    def calc_monthly_metrics(start_w, end_w):
        if start_w < 1 or end_w < 1 or start_w > end_w:
            return None
            
        # Kehadiran
        p_qs = semua_presensi.filter(minggu_ke__gte=start_w, minggu_ke__lte=end_w)
        p_tot = p_qs.count()
        p_hadir = p_qs.filter(status=PresensiSiswa.StatusChoices.HADIR).count()
        kehadiran = (p_hadir / p_tot * 100) if p_tot > 0 else None

        # Study Time (Rata-rata dari total jam mingguan)
        w_sums = []
        for week in range(start_w, end_w + 1):
            s = semua_study.filter(minggu_ke=week).aggregate(tot=Sum('studytime'))['tot'] or 0.0
            w_sums.append(s)
        study_time = (sum(w_sums) / len(w_sums)) if w_sums else None

        # Nilai Formatif
        n_qs = semua_nilai.filter(minggu_ke__gte=start_w, minggu_ke__lte=end_w)
        pre = n_qs.filter(jenis_evaluasi=NilaiSiswa.EvaluasiChoices.QUIZ).aggregate(avg=Avg('skor'))['avg']
        ass = n_qs.filter(jenis_evaluasi=NilaiSiswa.EvaluasiChoices.TUGAS).aggregate(avg=Avg('skor'))['avg']
        post = n_qs.filter(jenis_evaluasi=NilaiSiswa.EvaluasiChoices.QUIZ2).aggregate(avg=Avg('skor'))['avg']

        return {"kehadiran": kehadiran, "study_time": study_time, "pretest": pre, "assessment": ass, "posttest": post}

    def build_komparasi_node(val_curr, val_prev):
        sekarang = val_curr if val_curr is not None else 0.0
        
        if val_prev is None:
            return {"sekarang": round(sekarang, 1), "bulan_lalu": None, "selisih": None, "tren": None}
            
        bulan_lalu = val_prev
        selisih = sekarang - bulan_lalu
        
        if selisih > 0: tren = "positif"
        elif selisih < 0: tren = "negatif"
        else: tren = "netral"
        
        return {
            "sekarang": round(sekarang, 1),
            "bulan_lalu": round(bulan_lalu, 1),
            "selisih": round(selisih, 1),
            "tren": tren
        }

    # Hitung batas jendela waktu (Window)
    curr_end = minggu_terbaru
    curr_start = max(1, minggu_terbaru - 3)
    prev_end = curr_start - 1
    prev_start = prev_end - 3

    metrics_curr = calc_monthly_metrics(curr_start, curr_end) or {}
    metrics_prev = calc_monthly_metrics(prev_start, prev_end)

    komparasi_bulanan = {
        "kehadiran": build_komparasi_node(metrics_curr.get("kehadiran"), metrics_prev.get("kehadiran") if metrics_prev else None),
        "study_time": build_komparasi_node(metrics_curr.get("study_time"), metrics_prev.get("study_time") if metrics_prev else None),
        "pretest": build_komparasi_node(metrics_curr.get("pretest"), metrics_prev.get("pretest") if metrics_prev else None),
        "assessment": build_komparasi_node(metrics_curr.get("assessment"), metrics_prev.get("assessment") if metrics_prev else None),
        "posttest": build_komparasi_node(metrics_curr.get("posttest"), metrics_prev.get("posttest") if metrics_prev else None),
    }

    # 6. Analisis EWS Khusus Orang Tua
    pred_obj = PredictionResult.objects.filter(
        siswa=siswa, mapel=mapel_aktif, semester=active_semester, minggu_ke=minggu_terbaru
    ).first()
    
    if pred_obj:
        status_risiko = pred_obj.get_risk_score_display().upper()
        label_risiko_display = f"Risiko {status_risiko.capitalize()}"
        
        rekomendasi_mentah = pred_obj.recommendation
        rekomendasi_list = []
        if isinstance(rekomendasi_mentah, dict) and "orang_tua" in rekomendasi_mentah:
            rek_teks = rekomendasi_mentah["orang_tua"]
            rekomendasi_list = [kalimat.strip() for kalimat in rek_teks.split('.') if kalimat.strip()]
        else:
            rekomendasi_list = [str(rekomendasi_mentah)]
    else:
        status_risiko = "LOW"
        label_risiko_display = "Risiko Rendah (Aman)"
        rekomendasi_list = ["Belum ada data analisis AI minggu ini. Tetap dampingi belajar anak Anda."]

    return {
        "profil": profil_data,
        "mapel_aktif": {"id": mapel_aktif.id, "nama_mapel": mapel_aktif.nama_mapel},
        "filter_opsi_mapel": filter_opsi_mapel,
        "grafik_mingguan": grafik_mingguan,
        "komparasi_bulanan": komparasi_bulanan,
        "analisis_ews": {
            "status_risiko": status_risiko,
            "label_risiko_display": label_risiko_display,
            "rekomendasi_orangtua": rekomendasi_list
        }
    }