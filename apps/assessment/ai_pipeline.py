from typing import List
from django.db import transaction, IntegrityError
from assessment.models import NilaiSiswa, PresensiSiswa, HistoriStudytime, PredictionResult
from academic.models import Siswa, MataPelajaran
from assessment.ml.predict import predict_student
from assessment.llm import generate_batch_recommendations

def process_batch_ews_pipeline(list_nisn: List[str], mapel_id: int, semester_id: int, minggu_ke: int) -> List[PredictionResult]:
    # 1. Filter Idempotensi (Hanya proses siswa yang belum memiliki PredictionResult minggu ini)
    existing_nisns = PredictionResult.objects.filter(
        mapel_id=mapel_id, semester_id=semester_id, minggu_ke=minggu_ke, siswa__nisn__in=list_nisn
    ).values_list('siswa__nisn', flat=True)
    
    nisn_to_process = [nisn for nisn in list_nisn if nisn not in existing_nisns]
    if not nisn_to_process:
        return []  # Semua siswa di batch ini sudah diproses sebelumnya
        
    mapel = MataPelajaran.objects.filter(id=mapel_id).first()
    mapel_nama = mapel.nama_mapel if mapel else "Umum"
    
    low_risk_objects = []
    needs_ai_batch = []
    ai_siswa_map = {} 
    
    # 2. Iterasi & Eksekusi ML (Scikit-Learn sangat cepat, bisa di-loop)
    for nisn in nisn_to_process:
        siswa = Siswa.objects.filter(nisn=nisn).first()
        if not siswa: continue

        nilai_qs = NilaiSiswa.objects.filter(siswa=siswa, mapel_id=mapel_id, semester_id=semester_id, minggu_ke=minggu_ke)
        quizzes = nilai_qs.filter(jenis_evaluasi=NilaiSiswa.EvaluasiChoices.QUIZ).order_by('id')
        quiz_1 = quizzes[0] if quizzes.count() > 0 else None
        quiz_2 = nilai_qs.filter(jenis_evaluasi='QUIZ2').first()
        if not quiz_2 and quizzes.count() > 1:
            quiz_2 = quizzes[1]

        tugas = nilai_qs.filter(jenis_evaluasi=NilaiSiswa.EvaluasiChoices.TUGAS).first()
        st_obj = HistoriStudytime.objects.filter(siswa=siswa, mapel_id=mapel_id, semester_id=semester_id, minggu_ke=minggu_ke).first()
        daily_study_hours = round(st_obj.studytime / 7.0, 1) if st_obj else 0.0

        presensi_qs = PresensiSiswa.objects.filter(siswa=siswa, mapel_id=mapel_id, semester_id=semester_id, minggu_ke__lte=minggu_ke)
        total_hari = presensi_qs.count()
        hadir = presensi_qs.filter(status=PresensiSiswa.StatusChoices.HADIR).count()
        attendance_pct = (hadir / total_hari * 100) if total_hari > 0 else 100.0

        q1_score = quiz_1.skor if quiz_1 else 0.0
        q2_score = quiz_2.skor if quiz_2 else 0.0
        tugas_score = tugas.skor if tugas else 0.0

        # ML Predict
        ml_result = predict_student(
            attendance=attendance_pct, quiz_1_score_pct=q1_score,
            quiz_2_score_pct=q2_score, assignment_pct=tugas_score, daily_study_hours=daily_study_hours
        )
        risk_label = ml_result["risk"]
        
        # Pemisahan Jalur (Bypass LLM vs Butuh LLM)
        if risk_label == "Low Risk":
            low_risk_objects.append(
                PredictionResult(
                    siswa=siswa, mapel_id=mapel_id, semester_id=semester_id, minggu_ke=minggu_ke,
                    risk_score=PredictionResult.RiskChoices.LOW,
                    recommendation={
                        "guru": f"Pemahaman konsep {mapel_nama} sangat baik (>90). Pertahankan metode Anda.",
                        "orangtua": f"Luar biasa! Anak Anda berprestasi di {mapel_nama}. Berikan apresiasi.",
                        "siswa": f"Kerja bagus di {mapel_nama}! Pertahankan kedisiplinanmu."
                    }
                )
            )
        else:
            # Masukkan ke keranjang antrean LLM
            needs_ai_batch.append({
                "nisn": nisn, "nama": siswa.nama, "mapel": mapel_nama, "risk_level": risk_label,
                "attendance": attendance_pct, "quiz_1_score_pct": q1_score, "quiz_2_score_pct": q2_score,
                "assignment_pct": tugas_score, "daily_study_hours": daily_study_hours
            })
            ai_siswa_map[nisn] = siswa
            
    # 3. Proses LLM dengan Chunking (Maksimal 5 Siswa per Request)
    ai_results_objects = []
    CHUNK_SIZE = 15
    
    for i in range(0, len(needs_ai_batch), CHUNK_SIZE):
        chunk = needs_ai_batch[i:i + CHUNK_SIZE]
        
        # Panggil Gemini 1 kali untuk 15 siswa
        batch_recs = generate_batch_recommendations(chunk)
        
        for nisn, rec_json in batch_recs.items():
            siswa = ai_siswa_map[nisn]
            # Cari risk level asli dari chunk
            risk_str = next(item["risk_level"] for item in chunk if item["nisn"] == nisn)
            risk_int = PredictionResult.RiskChoices.HIGH if risk_str == "High Risk" else PredictionResult.RiskChoices.MEDIUM
            
            ai_results_objects.append(
                PredictionResult(
                    siswa=siswa, mapel_id=mapel_id, semester_id=semester_id, minggu_ke=minggu_ke,
                    risk_score=risk_int, recommendation=rec_json
                )
            )

    # 4. Penyimpanan Massal yang Aman dari DB Crash
    all_results = low_risk_objects + ai_results_objects
    if all_results:
        try:
            with transaction.atomic():
                PredictionResult.objects.bulk_create(all_results)
        except IntegrityError as e:
            print(f"DB Error saat bulk insert EWS: {e}")
            
    return all_results