from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg, Max

from academic.models import Siswa
from assessment.models import (
    PredictionResult, 
    PresensiSiswa, 
    NilaiSiswa
)


class DashboardSummaryView(APIView):
    def get(self, request):
        # 1. Tangkap parameter angkatan dari URL (?angkatan=2025)
        angkatan = request.query_params.get('angkatan')

        # Filter Siswa dasar
        siswa_qs = Siswa.objects.all()
        if angkatan:
            siswa_qs = siswa_qs.filter(angkatan=angkatan)

        total_siswa = siswa_qs.count()

        # 2. Ambil minggu ke berapa data prediksi paling baru
        latest_week = PredictionResult.objects.aggregate(
            max_w=Max('minggu_ke')
        )['max_w'] or 1

        # 3. Filter Prediksi Minggu Terakhir sesuai siswa_qs
        latest_preds = PredictionResult.objects.filter(
            siswa__in=siswa_qs, 
            minggu_ke=latest_week
        )
        
        high_count = latest_preds.filter(risk_score=PredictionResult.RiskChoices.HIGH).count()
        med_count = latest_preds.filter(risk_score=PredictionResult.RiskChoices.MEDIUM).count()
        low_count = latest_preds.filter(risk_score=PredictionResult.RiskChoices.LOW).count()

        total_preds = high_count + med_count + low_count or 1

        # 4. Kehadiran Global (%) sesuai siswa_qs
        presensi_qs = PresensiSiswa.objects.filter(siswa__in=siswa_qs)
        total_presensi = presensi_qs.count()
        hadir_presensi = presensi_qs.filter(status=PresensiSiswa.StatusChoices.HADIR).count()
        avg_presensi_global = round((hadir_presensi / total_presensi * 100), 2) if total_presensi > 0 else 0.0

        # 5. Trend Performa Per Minggu sesuai siswa_qs
        nilai_qs = NilaiSiswa.objects.filter(siswa__in=siswa_qs)
        trend_performa = []
        
        for w in range(1, latest_week + 1):
            avg_n = nilai_qs.filter(minggu_ke=w).aggregate(avg=Avg('skor'))['avg'] or 0.0
            
            p_w = presensi_qs.filter(minggu_ke=w)
            p_total = p_w.count()
            p_hadir = p_w.filter(status=PresensiSiswa.StatusChoices.HADIR).count()
            avg_p = (p_hadir / p_total * 100) if p_total > 0 else 0.0

            trend_performa.append({
                "minggu_ke": w,
                "label": f"Minggu {w}",
                "rata_rata_nilai": round(avg_n, 1),
                "rata_rata_presensi": round(avg_p, 1)
            })

        # 6. Proporsi Risiko
        proporsi_risiko = {
            "rendah": {
                "count": low_count,
                "percentage": round((low_count / total_preds) * 100, 1)
            },
            "sedang": {
                "count": med_count,
                "percentage": round((med_count / total_preds) * 100, 1)
            },
            "tinggi": {
                "count": high_count,
                "percentage": round((high_count / total_preds) * 100, 1)
            }
        }

        # 7. Top Intervensi (Filtered)
        high_risk_preds = (
            latest_preds.filter(risk_score=PredictionResult.RiskChoices.HIGH)
            .select_related('siswa', 'siswa__kelas')[:5]
        )

        top_intervensi = []
        for pred in high_risk_preds:
            s = pred.siswa
            s_nilai = nilai_qs.filter(siswa=s).aggregate(avg=Avg('skor'))['avg'] or 0.0
            
            s_p_total = presensi_qs.filter(siswa=s).count()
            s_p_hadir = presensi_qs.filter(siswa=s, status=PresensiSiswa.StatusChoices.HADIR).count()
            s_kehadiran = (s_p_hadir / s_p_total * 100) if s_p_total > 0 else 0.0

            top_intervensi.append({
                "nisn": s.nisn,
                "nama": s.nama,
                "kelas": s.kelas.nama_kelas if s.kelas else "-",
                "nilai": round(s_nilai, 1),
                "kehadiran": round(s_kehadiran, 1),
                "status_risk": "HIGH"
            })

        return Response({
            "success": True,
            "data": {
                "summary": {
                    "total_siswa": total_siswa,
                    "risiko_tinggi": high_count,
                    "risiko_sedang": med_count,
                    "rata_rata_presensi": avg_presensi_global
                },
                "trend_performa": trend_performa,
                "proporsi_risiko": proporsi_risiko,
                "top_intervensi": top_intervensi
            }
        }, status=status.HTTP_200_OK)