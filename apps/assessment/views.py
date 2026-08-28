from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from assessment import selectors, services
from assessment.serializers import (
    BulkPresensiInputSerializer,
    HistoriStudytimeInputSerializer,
    HistoriStudytimeOutputSerializer,
    NilaiSiswaInputSerializer,
    NilaiSiswaOutputSerializer,
    PredictionResultInputSerializer,
    PredictionResultOutputSerializer,
    PresensiSiswaOutputSerializer,
)


class HistoriStudytimeListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

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

    def post(self, request):
        serializer = HistoriStudytimeInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        record = services.record_studytime(**serializer.validated_data)
        output_serializer = HistoriStudytimeOutputSerializer(record)
        return Response(
            {"success": True, "message": "Data studytime berhasil disimpan", "data": output_serializer.data},
            status=status.HTTP_201_CREATED,
        )


class NilaiSiswaListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

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

    def post(self, request):
        serializer = NilaiSiswaInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nilai = services.create_nilai_siswa(**serializer.validated_data)
        output_serializer = NilaiSiswaOutputSerializer(nilai)
        return Response(
            {"success": True, "message": "Nilai siswa berhasil dicatat", "data": output_serializer.data},
            status=status.HTTP_201_CREATED,
        )


class PresensiBulkCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

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

    def post(self, request):
        serializer = BulkPresensiInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        presensi_records = services.bulk_record_presensi(**serializer.validated_data)
        output_serializer = PresensiSiswaOutputSerializer(presensi_records, many=True)
        return Response(
            {"success": True, "message": "Presensi kelas berhasil disimpan", "data": output_serializer.data},
            status=status.HTTP_201_CREATED,
        )


class PredictionResultListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

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