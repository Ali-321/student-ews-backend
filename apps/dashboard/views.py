from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.core.utils.permissions import IsGuruRole, IsOrangTuaRole, IsSiswaRole
from apps.dashboard.selectors import get_dashboard_ortu_summary, get_dashboard_siswa_summary, get_dashboard_summary, get_school_analytics
from apps.dashboard.serializers import (
    DashboardSummaryResponseSerializer,
    SchoolAnalyticsResponseSerializer,
    DashboardSiswaResponseSerializer,
    DashboardOrtuResponseSerializer,
    
)



class DashboardSummaryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsGuruRole]

    @extend_schema(
        summary='Ambil Ringkasan Dashboard EWS',
        description=(
            'Mengembalikan agregasi data ringkasan siswa, tren performa'
            ' mingguan, proporsi tingkat risiko, insight kelas berisiko/aman,'
            ' dan 5 siswa teratas yang membutuhkan intervensi. Mendukung filter global.'
        ),
        parameters=[
            OpenApiParameter(
                name='kelas_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filter ID kelas (Opsional, memengaruhi metrik global)',
            ),
            OpenApiParameter(
                name='mapel_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filter ID mata pelajaran (Opsional, memengaruhi metrik global)',
            ),
        ],
        responses={200: DashboardSummaryResponseSerializer},
    )
    def get(self, request):
        kelas_id = request.query_params.get('kelas_id')
        mapel_id = request.query_params.get('mapel_id')

        kelas_id = int(kelas_id) if kelas_id and kelas_id.isdigit() else None
        mapel_id = int(mapel_id) if mapel_id and mapel_id.isdigit() else None

        data = get_dashboard_summary(kelas_id=kelas_id, mapel_id=mapel_id)
        return Response(
            {'success': True, 'data': data}, status=status.HTTP_200_OK
        )


class DashboardAnalyticsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsGuruRole]

    @extend_schema(
        summary='Ambil Laporan Analitis & Statistik Sekolah',
        description=(
            'Mengembalikan komparasi jumlah siswa berisiko per kelas dan'
            ' persentase agregat faktor pemicu risiko ML. Menyediakan opsi'
            ' filter kelas dan mapel.'
        ),
        parameters=[
            OpenApiParameter(
                name='kelas_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filter ID kelas (Opsional, default: seluruh kelas)',
            ),
            OpenApiParameter(
                name='mapel_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filter ID mata pelajaran (Opsional, default: seluruh mapel)',
            ),
        ],
        responses={200: SchoolAnalyticsResponseSerializer},
    )
    def get(self, request):
        kelas_id = request.query_params.get('kelas_id')
        mapel_id = request.query_params.get('mapel_id')

        kelas_id = int(kelas_id) if kelas_id and kelas_id.isdigit() else None
        mapel_id = int(mapel_id) if mapel_id and mapel_id.isdigit() else None

        data = get_school_analytics(kelas_id=kelas_id, mapel_id=mapel_id)
        return Response(
            {'success': True, 'data': data}, status=status.HTTP_200_OK
        )

class DashboardSiswaView(APIView):
    permission_classes = [IsSiswaRole] 

    @extend_schema(
        tags=["Dashboard"],
        summary='Ambil Data Dashboard Spesifik Siswa',
        description='Menyajikan metrik performa mingguan terbaru, presensi harian, nilai, dan analisis EWS untuk satu mata pelajaran spesifik. Secara default akan memuat mapel pertama jika parameter mapel_id tidak dikirim.',
        parameters=[
            OpenApiParameter(
                name='mapel_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filter Mapel (Jika kosong, backend akan memilih default mapel secara otomatis)',
            ),
        ],
        responses={200: DashboardSiswaResponseSerializer},
    )
    def get(self, request, siswa_nisn: str):
        mapel_id = request.query_params.get('mapel_id')
        mapel_id = int(mapel_id) if mapel_id and mapel_id.isdigit() else None

        try:
            data = get_dashboard_siswa_summary(siswa_nisn=siswa_nisn, mapel_id=mapel_id)
            
            return Response(
                {
                    'success': True,
                    'message': 'Data dashboard siswa berhasil diambil.',
                    'data': data
                }, 
                status=status.HTTP_200_OK
            )
        except ValueError as e:
             # Menangkap error jika tabel mapel di sistem masih benar-benar kosong
             return Response(
                {'success': False, 'message': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class DashboardOrangTuaView(APIView):
    permission_classes = [IsOrangTuaRole]

    @extend_schema(
        tags=["Dashboard"],
        summary='Ambil Data Tren Grafik untuk Orang Tua',
        description='Menyajikan data deret waktu (Time-Series) mingguan per mapel yang dikunci pada Semester Aktif berjalan. Termasuk tren absensi, jam belajar (kumulatif), riwayat nilai, dan rekomendasi khusus orang tua.',
        parameters=[
            OpenApiParameter(
                name='mapel_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filter Mapel (Jika kosong, backend memilih default secara otomatis)',
            ),
        ],
        responses={200: DashboardOrtuResponseSerializer},
    )
    def get(self, request, siswa_nisn: str):
        mapel_id = request.query_params.get('mapel_id')
        mapel_id = int(mapel_id) if mapel_id and mapel_id.isdigit() else None

        try:
            data = get_dashboard_ortu_summary(siswa_nisn=siswa_nisn, mapel_id=mapel_id)
            
            return Response(
                {
                    'success': True,
                    'message': 'Data tren mingguan orang tua berhasil diambil.',
                    'data': data
                }, 
                status=status.HTTP_200_OK
            )
        except ValueError as e:
             return Response(
                {'success': False, 'message': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )