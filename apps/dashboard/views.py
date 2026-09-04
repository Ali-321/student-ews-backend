from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.core.permissions import IsGuruRole
from apps.dashboard.selectors import get_dashboard_summary, get_school_analytics
from apps.dashboard.serializers import (
    DashboardSummaryResponseSerializer,
    SchoolAnalyticsResponseSerializer,
)


class DashboardSummaryView(APIView):
  authentication_classes = [JWTAuthentication]
  permission_classes = [IsGuruRole]

  @extend_schema(
      summary='Ambil Ringkasan Dashboard EWS',
      description=(
          'Mengembalikan agregasi data ringkasan siswa, tren performa'
          ' mingguan, proporsi tingkat risiko, insight kelas berisiko/aman,'
          ' dan 5 siswa teratas yang membutuhkan intervensi.'
      ),
      responses={200: DashboardSummaryResponseSerializer},
  )
  def get(self, request):
    data = get_dashboard_summary()
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
              description=(
                  'Filter ID mata pelajaran (Opsional, default: seluruh mapel)'
              ),
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