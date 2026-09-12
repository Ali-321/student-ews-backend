from django.shortcuts import render
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes, inline_serializer

from assessment.serializers.inputs import BulkAssessmentInputSerializer


from apps.core.utils.pagination import SiswaPagination, get_paginated_response
from assessment import selectors, services
from assessment.serializers import (
    BulkPresensiInputSerializer,
    HistoriStudytimeInputSerializer,
    HistoriStudytimeOutputSerializer,
    NilaiSiswaOutputSerializer,
    PredictionResultInputSerializer,
    PredictionResultOutputSerializer,
    PresensiSiswaOutputSerializer,
    StatusChoiceOutputSerializer,
    SiswaHybridRiskOutputSerializer,
)


class HistoriStudytimeListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

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


class PresensiBulkCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Assessment - Presensi"],
        summary="Mendapatkan daftar presensi siswa",
        parameters=[
            OpenApiParameter("siswa_nisn", OpenApiTypes.STR, description="NISN Siswa"),
            OpenApiParameter("mapel_id", OpenApiTypes.INT, description="ID Mata Pelajaran"),
            OpenApiParameter("semester_id", OpenApiTypes.INT, description="ID Semester"),
            OpenApiParameter("status", OpenApiTypes.STR, description="Status Kehadiran (HADIR, ALPA, SAKIT, IZIN)"),
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


class NilaiSiswaListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Assessment - Nilai & Assessment"],
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
        tags=["Assessment - Nilai & Assessment"],
        summary="Simpan data matriks assessment (study time & nilai) secara bulk",
        request=BulkAssessmentInputSerializer,
        responses={201: NilaiSiswaOutputSerializer(many=True)},
    )
    def post(self, request):
        serializer = BulkAssessmentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = services.bulk_record_assessment(**serializer.validated_data)
        output_serializer = NilaiSiswaOutputSerializer(result["nilai_records"], many=True)
        return Response(
            {
                "success": True,
                "message": "Data assessment (study time & nilai) berhasil disimpan",
                "data": output_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class PredictionResultListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Assessment - Prediksi EWS - ini nanti akan di Hapus -"],
        summary="Mendapatkan daftar hasil prediksi EWS",
        parameters=[
            OpenApiParameter("siswa_nisn", OpenApiTypes.STR, description="NISN Siswa"),
            OpenApiParameter("mapel_id", OpenApiTypes.INT, description="ID Mata Pelajaran"),
            OpenApiParameter("semester_id", OpenApiTypes.INT, description="ID Semester"),
            OpenApiParameter("risk_score", OpenApiTypes.STR, description="Tingkat Risiko (LOW, MEDIUM, HIGH)"),
            OpenApiParameter("minggu_ke", OpenApiTypes.INT, description="Minggu ke-"),
        ],
        responses={200: PredictionResultOutputSerializer(many=True)},
    )
    def get(self, request):
        filters = {
            "siswa_nisn": request.query_params.get("siswa_nisn"),
            "mapel_id": request.query_params.get("mapel_id"),
            "semester_id": request.query_params.get("semester_id"),
            "risk_score": request.query_params.get("risk_score"),
            "minggu_ke": request.query_params.get("minggu_ke"),
        }
        filters = {k: v for k, v in filters.items() if v is not None}
        prediction_qs = selectors.prediction_result_list(filters=filters)
        serializer = PredictionResultOutputSerializer(prediction_qs, many=True)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Assessment - Prediksi EWS - ini nanti akan di Hapus -"],
        summary="Mencatat hasil prediksi EWS",
        request=PredictionResultInputSerializer,
        responses={201: PredictionResultOutputSerializer},
    )
    def post(self, request):
        serializer = PredictionResultInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        prediction = services.record_prediction_result(**serializer.validated_data)
        output_serializer = PredictionResultOutputSerializer(prediction)
        return Response(
            {"success": True, "message": "Hasil prediksi EWS berhasil disimpan", "data": output_serializer.data},
            status=status.HTTP_201_CREATED,
        )


class RingkasanAkademikSiswaAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Assessment - Ringkasan Akademik"],
        summary="Mendapatkan ringkasan akademik siswa",
        parameters=[
            OpenApiParameter(
                name="semester_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID Semester (Wajib)",
            )
        ],
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
        },
    )
    def get(self, request, siswa_nisn):
        semester_id = request.query_params.get("semester_id")
        if not semester_id:
            return Response(
                {"success": False, "error": "Query parameter 'semester_id' wajib diisi"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ringkasan = selectors.get_ringkasan_akademik_siswa(
            siswa_nisn=siswa_nisn, semester_id=int(semester_id)
        )
        return Response({"success": True, "data": ringkasan}, status=status.HTTP_200_OK)

    
class StatusChoicesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Assessment - Presensi"],
        summary="Mendapatkan daftar status presensi siswa",
        description="Mengembalikan daftar enum pilihan status presensi siswa untuk dropdown UI.",
        responses={
            200: inline_serializer(
                name="PresensiStatusChoicesResponse",
                fields={
                    "success": serializers.BooleanField(default=True),
                    "data": StatusChoiceOutputSerializer(many=True),
                },
            )
        },
    )
    def get(self, request):
        status_choices = selectors.get_presensi_status_choices()
        serializer = StatusChoiceOutputSerializer(status_choices, many=True)
        return Response(
            {"success": True, "data": serializer.data},
            status=status.HTTP_200_OK,
        )


# ==================== Halaman Daftar Siswa ====================

class SiswaRiskSummaryListApi(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Assessment - EWS (Untuk Halaman Daftar Siswa) catatan: semester_id optional, jika tidak diberikan akan otomatis mengambil semester aktif"],
        summary="Mendapatkan daftar rekap risiko siswa (Paginated)",
        description="Mengambil data rekap siswa berpaginasi dengan filter pencarian nama/NISN, kelas, dan status risiko.",
        parameters=[
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Nomor halaman (Default: 1)",
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Jumlah baris per halaman (Default: 10, Max: 100)",
            ),
            OpenApiParameter(
                name="semester_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter ID Semester",
            ),
            OpenApiParameter(
                name="kelas_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Filter ID Kelas",
            ),
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Pencarian Nama Siswa atau NISN",
            ),
            OpenApiParameter(
                name="risk_status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                enum=["HIGH", "MEDIUM", "LOW", "Tinggi", "Sedang", "Rendah"],
                description="Filter status risiko",
            ),
        ],
        responses={200: SiswaHybridRiskOutputSerializer(many=True)},
    )
    def get(self, request):
        semester_id = request.query_params.get("semester_id")
        kelas_id = request.query_params.get("kelas_id")
        search = request.query_params.get("search")
        risk_status = request.query_params.get("risk_status")

        if risk_status:
            status_map = {
                "tinggi": "HIGH",
                "sedang": "MEDIUM",
                "rendah": "LOW",
            }
            risk_status = status_map.get(risk_status.lower(), risk_status)

        siswa_queryset = selectors.get_siswa_with_hybrid_risk_selector(
            semester_id=int(semester_id) if semester_id and semester_id.isdigit() else None,
            kelas_id=int(kelas_id) if kelas_id and kelas_id.isdigit() else None,
            search=search,
            risk_status=risk_status,
        )

        return get_paginated_response(
            pagination_class=SiswaPagination,
            serializer_class=SiswaHybridRiskOutputSerializer,
            queryset=siswa_queryset,
            request=request,
            view=self,
        )