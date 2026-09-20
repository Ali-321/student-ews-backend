from django.shortcuts import get_object_or_404
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, inline_serializer

from apps.core.utils.pagination import SiswaPagination, get_paginated_response
from apps.core.utils.permissions import IsAdminRole, IsGuruRole
from assessment import selectors, services
from assessment.models import PredictionResult
from assessment.serializers import (
    BulkAssessmentInputSerializer,
    BulkPresensiInputSerializer,
    HistoriStudytimeInputSerializer,
    HistoriStudytimeOutputSerializer,
    NilaiSiswaOutputSerializer,
    PredictionResultOutputSerializer,
    PresensiSiswaOutputSerializer,
    StatusChoiceOutputSerializer,
    SiswaHybridRiskOutputSerializer,
    SiswaRiskDetailResponseSerializer
)


# ==========================================
# 1. STUDY TIME DOMAIN
# ==========================================
class HistoriStudytimeListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    permission_classes = [IsGuruRole]

    @extend_schema(
        tags=["Assessment - Study Time"],
        summary="Mendapatkan daftar histori studytime siswa",
        parameters=[
            OpenApiParameter("siswa_nisn", OpenApiTypes.STR, description="NISN Siswa"),
            OpenApiParameter("mapel_id", OpenApiTypes.INT, description="ID Mata Pelajaran"),
            OpenApiParameter("semester_id", OpenApiTypes.INT, description="ID Semester"),
            OpenApiParameter("minggu_ke", OpenApiTypes.INT, description="Minggu ke-"),
        ],
        responses={200: HistoriStudytimeOutputSerializer(many=True)},
    )
    def get(self, request):
        filters = {
            "siswa_nisn": request.query_params.get("siswa_nisn"),
            "mapel_id": request.query_params.get("mapel_id"),
            "semester_id": request.query_params.get("semester_id"),
            "minggu_ke": request.query_params.get("minggu_ke"),
        }
        filters = {k: v for k, v in filters.items() if v is not None}
        studytime_qs = selectors.histori_studytime_list(filters=filters)
        serializer = HistoriStudytimeOutputSerializer(studytime_qs, many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Assessment - Study Time"],
        summary="Mencatat data studytime siswa",
        request=HistoriStudytimeInputSerializer,
        responses={201: HistoriStudytimeOutputSerializer},
    )
    def post(self, request):
        serializer = HistoriStudytimeInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        record = services.record_studytime(**serializer.validated_data)
        output_serializer = HistoriStudytimeOutputSerializer(record)
        return Response(
            {"success": True, "message": "Data studytime berhasil disimpan", "data": output_serializer.data},
            status=status.HTTP_201_CREATED,
        )


# ==========================================
# 2. NILAI DOMAIN
# ==========================================
class NilaiSiswaListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    permission_classes = [IsGuruRole] 
    

    @extend_schema(
        tags=["Assessment - Nilai"],
        summary="Mendapatkan daftar nilai siswa",
        parameters=[
            OpenApiParameter("siswa_nisn", OpenApiTypes.STR, description="NISN Siswa"),
            OpenApiParameter("mapel_id", OpenApiTypes.INT, description="ID Mata Pelajaran"),
            OpenApiParameter("semester_id", OpenApiTypes.INT, description="ID Semester"),
            OpenApiParameter("jenis_evaluasi", OpenApiTypes.STR, description="Jenis Evaluasi (QUIZ, TUGAS, UTS, UAS)"),
            OpenApiParameter("minggu_ke", OpenApiTypes.INT, description="Minggu ke-"),
        ],
        responses={200: NilaiSiswaOutputSerializer(many=True)},
    )
    def get(self, request):
        filters = {
            "siswa_nisn": request.query_params.get("siswa_nisn"),
            "mapel_id": request.query_params.get("mapel_id"),
            "semester_id": request.query_params.get("semester_id"),
            "jenis_evaluasi": request.query_params.get("jenis_evaluasi"),
            "minggu_ke": request.query_params.get("minggu_ke"),
        }
        filters = {k: v for k, v in filters.items() if v is not None}
        nilai_qs = selectors.nilai_siswa_list(filters=filters)
        serializer = NilaiSiswaOutputSerializer(nilai_qs, many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Assessment - Nilai"],
        summary="Simpan data assessment & studytime secara bulk",
        request=BulkAssessmentInputSerializer,
        responses={201: inline_serializer(
            name="BulkAssessmentResponse",
            fields={
                "success": serializers.BooleanField(),
                "message": serializers.CharField(),
                "data": inline_serializer(
                    name="BulkAssessmentData",
                    fields={
                        "studytime_records": HistoriStudytimeOutputSerializer(many=True),
                        "nilai_records": NilaiSiswaOutputSerializer(many=True),
                    }
                )
            }
        )},
    )
    def post(self, request):
        serializer = BulkAssessmentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        results = services.bulk_record_assessment(**serializer.validated_data)

        studytime_serialized = HistoriStudytimeOutputSerializer(results["studytime_records"], many=True).data
        nilai_serialized = NilaiSiswaOutputSerializer(results["nilai_records"], many=True).data

        return Response(
            {
                "success": True,
                "message": "Data assessment & studytime berhasil disimpan",
                "data": {
                    "studytime_records": studytime_serialized,
                    "nilai_records": nilai_serialized,
                },
            },
            status=status.HTTP_201_CREATED,
        )


# ==========================================
# 3. PRESENSI DOMAIN
# ==========================================
class PresensiBulkCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole, IsGuruRole] 
    permission_classes = [IsGuruRole]
   
    @extend_schema(
        tags=["Assessment - Presensi"],
        summary="Mendapatkan daftar presensi siswa",
        parameters=[
            OpenApiParameter("siswa_nisn", OpenApiTypes.STR, description="NISN Siswa"),
            OpenApiParameter("mapel_id", OpenApiTypes.INT, description="ID Mata Pelajaran"),
            OpenApiParameter("semester_id", OpenApiTypes.INT, description="ID Semester"),
            OpenApiParameter("status", OpenApiTypes.STR, description="Status Kehadiran (Hadir, Alpa, Sakit, Izin)"),
            OpenApiParameter("minggu_ke", OpenApiTypes.INT, description="Minggu ke-"),
        ],
        responses={200: PresensiSiswaOutputSerializer(many=True)},
    )
    def get(self, request):
        filters = {
            "siswa_nisn": request.query_params.get("siswa_nisn"),
            "mapel_id": request.query_params.get("mapel_id"),
            "semester_id": request.query_params.get("semester_id"),
            "status": request.query_params.get("status"),
            "minggu_ke": request.query_params.get("minggu_ke"),
        }
        filters = {k: v for k, v in filters.items() if v is not None}
        presensi_qs = selectors.presensi_siswa_list(filters=filters)
        serializer = PresensiSiswaOutputSerializer(presensi_qs, many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Assessment - Presensi"],
        summary="Simpan presensi siswa secara bulk/periode",
        request=BulkPresensiInputSerializer,
        responses={201: PresensiSiswaOutputSerializer(many=True)},
    )
    def post(self, request):
        serializer = BulkPresensiInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        presensi_records = services.bulk_record_presensi(**serializer.validated_data)
        output_serializer = PresensiSiswaOutputSerializer(presensi_records, many=True)
        return Response(
            {
                "success": True,
                "message": "Presensi periode berhasil disimpan",
                "data": output_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class StatusChoicesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Assessment - Presensi"],
        summary="Mendapatkan daftar pilihan status presensi",
        responses={200: StatusChoiceOutputSerializer(many=True)},
    )
    def get(self, request):
        choices = selectors.get_presensi_status_choices()
        serializer = StatusChoiceOutputSerializer(choices, many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)


# ==========================================
# 4. RISK ANALYTICS / EWS DOMAIN
# ==========================================
class SiswaRiskSummaryListApi(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole] 
    permission_classes = [IsGuruRole]
   

    @extend_schema(
        tags=["Assessment - Risk Analytics"],
        summary="Mendapatkan daftar ringkasan risiko hybrid siswa (Paginated)",
        description="Mengembalikan list siswa lengkap dengan nilai rata-rata, presensi, dan status ML EWS terbaru secara super cepat.",
        parameters=[
            OpenApiParameter("kelas_id", OpenApiTypes.INT, description="ID Kelas"),
            OpenApiParameter("search", OpenApiTypes.STR, description="Cari nama atau NISN siswa"),
            OpenApiParameter("risk_status", OpenApiTypes.STR, description="Filter risiko: HIGH, MEDIUM, LOW"),
            OpenApiParameter("page", OpenApiTypes.INT, description="Nomor halaman"),
            OpenApiParameter("page_size", OpenApiTypes.INT, description="Jumlah item per halaman"),
        ],
        responses={200: SiswaHybridRiskOutputSerializer(many=True)},
    )
    def get(self, request):
        search = request.query_params.get("search", "").strip() or None
        risk_status = request.query_params.get("risk_status", "").strip() or None
        
        try:
            kelas_id = int(request.query_params.get("kelas_id"))
        except (TypeError, ValueError):
            kelas_id = None

        qs = selectors.get_siswa_risk_summary_qs(
            kelas_id=kelas_id,
            search=search,
            risk_status=risk_status,
        )

        paginator = SiswaPagination()
        page = paginator.paginate_queryset(qs, request, view=self)

        if page is not None:
            # INJEKSI DATA MEMORI HANYA UNTUK 10 HALAMAN INI
            page = selectors.attach_metrics_to_paginated_siswa(page)
            serializer = SiswaHybridRiskOutputSerializer(page, many=True)
            
            # Kita tidak pakai helper get_paginated_response karena OrderedDict-nya berbeda
            # Gunakan bawaan DRF
            return paginator.get_paginated_response(serializer.data)

        # Fallback
        qs_list = selectors.attach_metrics_to_paginated_siswa(list(qs))
        serializer = SiswaHybridRiskOutputSerializer(qs_list, many=True)
        return Response({
            "success": True, 
            "message": "Berhasil mengambil data ringkasan risiko siswa",
            "results": serializer.data
        }, status=status.HTTP_200_OK)


class DetailPrediksiEWSApi(APIView):
    permission_classes = [IsAuthenticated,IsAdminRole]
    permission_classes = [IsGuruRole]

    @extend_schema(
        tags=["Assessment - Risk Analytics"],
        summary="Mendapatkan detail rekomendasi GenAI per Siswa dan Mapel",
        responses={200: PredictionResultOutputSerializer}
    )
    def get(self, request, siswa_nisn: str, mapel_id: int, minggu_ke: int):
        prediksi = get_object_or_404(
            PredictionResult, 
            siswa__nisn=siswa_nisn, 
            mapel_id=mapel_id, 
            minggu_ke=minggu_ke
        )
        serializer = PredictionResultOutputSerializer(prediksi)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

class DetailProfilSiswaEWSApi(APIView):
    
    permission_classes = [IsAuthenticated, IsAdminRole] 
    permission_classes = [IsGuruRole]

    @extend_schema(
        tags=["Assessment - Risk Analytics"],
        summary="Mendapatkan detail profil dan metrik risiko siswa",
        description="Mengembalikan agregasi data akademik formatif (Murni 1 Minggu Terakhir) dan rekomendasi GenAI. Otomatis menampilkan Mapel pertama jika tidak ada filter.",
        parameters=[
            OpenApiParameter("mapel_id", OpenApiTypes.INT, location=OpenApiParameter.QUERY, description="ID Mata Pelajaran (Opsional, Default: Mapel Pertama)"),
        ],
        responses={200: SiswaRiskDetailResponseSerializer}
    )
    def get(self, request, siswa_nisn: str):
        mapel_id = request.query_params.get("mapel_id")
        mapel_id = int(mapel_id) if mapel_id and mapel_id.isdigit() else None

        try:
            # Mengambil data dari selector yang sudah mengembalikan mapel_aktif
            data = selectors.get_siswa_risk_detail(nisn=siswa_nisn, mapel_id=mapel_id)
            
            # DRF akan merender ini melalui SiswaRiskDetailResponseSerializer
            return Response(
                {
                    "success": True, 
                    "data": data
                }, 
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            # Proteksi jika database mapel kosong
            return Response(
                {"success": False, "message": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )