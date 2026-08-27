from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.pagination import LimitOffsetPagination, get_paginated_response
from core.permissions import IsAdminRole

from academic.selectors import (
    kelas_get_selector,
    kelas_list_selector,
    mapel_get_selector,
    mapel_list_selector,
    semester_get_selector,
    semester_list_selector,
    siswa_get_selector,
    siswa_list_selector,
    tahun_ajaran_get_selector,
    tahun_ajaran_list_selector,
)
from academic.serializers import (
    KelasInputSerializer,
    KelasOutputSerializer,
    KelasUpdateSerializer,
    MataPelajaranInputSerializer,
    MataPelajaranOutputSerializer,
    MataPelajaranUpdateSerializer,
    SemesterInputSerializer,
    SemesterOutputSerializer,
    SemesterUpdateSerializer,
    SiswaInputSerializer,
    SiswaOutputSerializer,
    SiswaUpdateSerializer,
    TahunAjaranInputSerializer,
    TahunAjaranOutputSerializer,
    TahunAjaranUpdateSerializer,
)
from academic.services import (
    kelas_create_service,
    kelas_delete_service,
    kelas_update_service,
    mapel_create_service,
    mapel_delete_service,
    mapel_update_service,
    semester_create_service,
    semester_delete_service,
    semester_update_service,
    siswa_create_service,
    siswa_delete_service,
    siswa_update_service,
    tahun_ajaran_create_service,
    tahun_ajaran_delete_service,
    tahun_ajaran_update_service,
)


# ==================== TAHUN AJARAN ====================
class TahunAjaranListCreateApi(APIView):
    permission_classes = [IsAdminRole]

    class Pagination(LimitOffsetPagination):
        default_limit = 10

    def get(self, request):
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=TahunAjaranOutputSerializer,
            queryset=tahun_ajaran_list_selector(),
            request=request,
            view=self,
        )

    def post(self, request):
        serializer = TahunAjaranInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ta = tahun_ajaran_create_service(**serializer.validated_data)
        return Response({"success": True, "message": "Tahun Ajaran berhasil dibuat.", "data": TahunAjaranOutputSerializer(ta).data}, status=status.HTTP_201_CREATED)


class TahunAjaranDetailApi(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request, pk: int):
        ta = tahun_ajaran_get_selector(id=pk)
        return Response({"success": True, "data": TahunAjaranOutputSerializer(ta).data}, status=status.HTTP_200_OK)

    def put(self, request, pk: int):
        ta = tahun_ajaran_get_selector(id=pk)
        serializer = TahunAjaranUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_ta = tahun_ajaran_update_service(instance=ta, **serializer.validated_data)
        return Response({"success": True, "message": "Tahun Ajaran diperbarui.", "data": TahunAjaranOutputSerializer(updated_ta).data}, status=status.HTTP_200_OK)

    def delete(self, request, pk: int):
        ta = tahun_ajaran_get_selector(id=pk)
        tahun_ajaran_delete_service(instance=ta)
        return Response({"success": True, "message": "Tahun Ajaran berhasil dihapus."}, status=status.HTTP_200_OK)


# ==================== SEMESTER ====================
class SemesterListCreateApi(APIView):
    permission_classes = [IsAdminRole]

    class Pagination(LimitOffsetPagination):
        default_limit = 10

    def get(self, request):
        ta_id = request.query_params.get("tahun_ajaran_id")
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=SemesterOutputSerializer,
            queryset=semester_list_selector(tahun_ajaran_id=ta_id),
            request=request,
            view=self,
        )

    def post(self, request):
        serializer = SemesterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sem = semester_create_service(**serializer.validated_data)
        return Response({"success": True, "message": "Semester berhasil dibuat.", "data": SemesterOutputSerializer(sem).data}, status=status.HTTP_201_CREATED)


class SemesterDetailApi(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request, pk: int):
        sem = semester_get_selector(id=pk)
        return Response({"success": True, "data": SemesterOutputSerializer(sem).data}, status=status.HTTP_200_OK)

    def put(self, request, pk: int):
        sem = semester_get_selector(id=pk)
        serializer = SemesterUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_sem = semester_update_service(instance=sem, **serializer.validated_data)
        return Response({"success": True, "message": "Semester diperbarui.", "data": SemesterOutputSerializer(updated_sem).data}, status=status.HTTP_200_OK)

    def delete(self, request, pk: int):
        sem = semester_get_selector(id=pk)
        semester_delete_service(instance=sem)
        return Response({"success": True, "message": "Semester berhasil dihapus."}, status=status.HTTP_200_OK)


# ==================== KELAS ====================
class KelasListCreateApi(APIView):
    permission_classes = [IsAdminRole]

    class Pagination(LimitOffsetPagination):
        default_limit = 10

    def get(self, request):
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=KelasOutputSerializer,
            queryset=kelas_list_selector(),
            request=request,
            view=self,
        )

    def post(self, request):
        serializer = KelasInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        kelas = kelas_create_service(**serializer.validated_data)
        return Response({"success": True, "message": "Kelas berhasil dibuat.", "data": KelasOutputSerializer(kelas).data}, status=status.HTTP_201_CREATED)


class KelasDetailApi(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request, pk: int):
        kelas = kelas_get_selector(id=pk)
        return Response({"success": True, "data": KelasOutputSerializer(kelas).data}, status=status.HTTP_200_OK)

    def put(self, request, pk: int):
        kelas = kelas_get_selector(id=pk)
        serializer = KelasUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_kelas = kelas_update_service(instance=kelas, **serializer.validated_data)
        return Response({"success": True, "message": "Kelas diperbarui.", "data": KelasOutputSerializer(updated_kelas).data}, status=status.HTTP_200_OK)

    def delete(self, request, pk: int):
        kelas = kelas_get_selector(id=pk)
        kelas_delete_service(instance=kelas)
        return Response({"success": True, "message": "Kelas berhasil dihapus."}, status=status.HTTP_200_OK)


# ==================== MATA PELAJARAN ====================
class MataPelajaranListCreateApi(APIView):
    permission_classes = [IsAdminRole]

    class Pagination(LimitOffsetPagination):
        default_limit = 10

    def get(self, request):
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=MataPelajaranOutputSerializer,
            queryset=mapel_list_selector(),
            request=request,
            view=self,
        )

    def post(self, request):
        serializer = MataPelajaranInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mapel = mapel_create_service(**serializer.validated_data)
        return Response({"success": True, "message": "Mata pelajaran berhasil dibuat.", "data": MataPelajaranOutputSerializer(mapel).data}, status=status.HTTP_201_CREATED)


class MataPelajaranDetailApi(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request, pk: int):
        mapel = mapel_get_selector(id=pk)
        return Response({"success": True, "data": MataPelajaranOutputSerializer(mapel).data}, status=status.HTTP_200_OK)

    def put(self, request, pk: int):
        mapel = mapel_get_selector(id=pk)
        serializer = MataPelajaranUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_mapel = mapel_update_service(instance=mapel, **serializer.validated_data)
        return Response({"success": True, "message": "Mata pelajaran diperbarui.", "data": MataPelajaranOutputSerializer(updated_mapel).data}, status=status.HTTP_200_OK)

    def delete(self, request, pk: int):
        mapel = mapel_get_selector(id=pk)
        mapel_delete_service(instance=mapel)
        return Response({"success": True, "message": "Mata pelajaran berhasil dihapus."}, status=status.HTTP_200_OK)


# ==================== SISWA ====================
class SiswaListCreateApi(APIView):
    permission_classes = [IsAdminRole]

    class Pagination(LimitOffsetPagination):
        default_limit = 10

    def get(self, request):
        kelas_id = request.query_params.get("kelas_id")
        angkatan = request.query_params.get("angkatan")
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=SiswaOutputSerializer,
            queryset=siswa_list_selector(kelas_id=kelas_id, angkatan=angkatan),
            request=request,
            view=self,
        )

    def post(self, request):
        serializer = SiswaInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        siswa = siswa_create_service(**serializer.validated_data)
        return Response({"success": True, "message": "Siswa berhasil dibuat.", "data": SiswaOutputSerializer(siswa).data}, status=status.HTTP_201_CREATED)


class SiswaDetailApi(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request, nisn: str):
        siswa = siswa_get_selector(nisn=nisn)
        return Response({"success": True, "data": SiswaOutputSerializer(siswa).data}, status=status.HTTP_200_OK)

    def put(self, request, nisn: str):
        siswa = siswa_get_selector(nisn=nisn)
        serializer = SiswaUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_siswa = siswa_update_service(instance=siswa, **serializer.validated_data)
        return Response({"success": True, "message": "Siswa diperbarui.", "data": SiswaOutputSerializer(updated_siswa).data}, status=status.HTTP_200_OK)

    def delete(self, request, nisn: str):
        siswa = siswa_get_selector(nisn=nisn)
        siswa_delete_service(instance=siswa)
        return Response({"success": True, "message": "Siswa berhasil dihapus."}, status=status.HTTP_200_OK)