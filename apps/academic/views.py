from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

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
from apps.core.utils.pagination import LimitOffsetPagination, get_paginated_response
from apps.core.utils.permissions import IsAdminRole, IsGuruRole


# ==================== TAHUN AJARAN ====================
@extend_schema(tags=["Tahun Ajaran"])
class TahunAjaranListCreateApi(APIView):
    permission_classes = [IsAdminRole]
    permission_classes = [IsGuruRole]
    
    class Pagination(LimitOffsetPagination):
        default_limit = 10

    @extend_schema(
        summary="Daftar Tahun Ajaran",
        description="Mengambil daftar tahun ajaran dengan paginasi limit-offset.",
        responses={200: TahunAjaranOutputSerializer(many=True)},
    )
    def get(self, request):
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=TahunAjaranOutputSerializer,
            queryset=tahun_ajaran_list_selector(),
            request=request,
            view=self,
        )

    @extend_schema(
        summary="Buat Tahun Ajaran Baru",
        request=TahunAjaranInputSerializer,
        responses={201: TahunAjaranOutputSerializer},
    )
    def post(self, request):
        serializer = TahunAjaranInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ta = tahun_ajaran_create_service(**serializer.validated_data)
        return Response(
            {
                "success": True,
                "message": "Tahun Ajaran berhasil dibuat.",
                "data": TahunAjaranOutputSerializer(ta).data,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Tahun Ajaran"])
class TahunAjaranDetailApi(APIView):
    permission_classes = [IsAdminRole]
    permission_classes = [IsGuruRole]

    @extend_schema(
        summary="Detail Tahun Ajaran",
        responses={200: TahunAjaranOutputSerializer},
    )
    def get(self, request, pk: int):
        ta = tahun_ajaran_get_selector(id=pk)
        return Response(
            {"success": True, "data": TahunAjaranOutputSerializer(ta).data},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Perbarui Tahun Ajaran",
        request=TahunAjaranUpdateSerializer,
        responses={200: TahunAjaranOutputSerializer},
    )
    def put(self, request, pk: int):
        ta = tahun_ajaran_get_selector(id=pk)
        serializer = TahunAjaranUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_ta = tahun_ajaran_update_service(instance=ta, **serializer.validated_data)
        return Response(
            {
                "success": True,
                "message": "Tahun Ajaran diperbarui.",
                "data": TahunAjaranOutputSerializer(updated_ta).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Hapus Tahun Ajaran",
        responses={200: None},
    )
    def delete(self, request, pk: int):
        ta = tahun_ajaran_get_selector(id=pk)
        tahun_ajaran_delete_service(instance=ta)
        return Response(
            {"success": True, "message": "Tahun Ajaran berhasil dihapus."},
            status=status.HTTP_200_OK,
        )


# ==================== SEMESTER ====================
@extend_schema(tags=["Semester"])
class SemesterListCreateApi(APIView):
    permission_classes = [IsAdminRole]
    permission_classes = [IsGuruRole]

    class Pagination(LimitOffsetPagination):
        default_limit = 10

    @extend_schema(
        summary="Daftar Semester",
        description="Mengambil daftar semester dengan opsi filter tahun ajaran.",
        parameters=[
            OpenApiParameter(
                name="tahun_ajaran_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter berdasarkan ID Tahun Ajaran",
                required=False,
            )
        ],
        responses={200: SemesterOutputSerializer(many=True)},
    )
    def get(self, request):
        ta_id = request.query_params.get("tahun_ajaran_id")
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=SemesterOutputSerializer,
            queryset=semester_list_selector(tahun_ajaran_id=ta_id),
            request=request,
            view=self,
        )

    @extend_schema(
        summary="Buat Semester Baru",
        request=SemesterInputSerializer,
        responses={201: SemesterOutputSerializer},
    )
    def post(self, request):
        serializer = SemesterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sem = semester_create_service(**serializer.validated_data)
        return Response(
            {
                "success": True,
                "message": "Semester berhasil dibuat.",
                "data": SemesterOutputSerializer(sem).data,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Semester"])
class SemesterDetailApi(APIView):
    permission_classes = [IsAdminRole]
    permission_classes = [IsGuruRole]

    @extend_schema(
        summary="Detail Semester",
        responses={200: SemesterOutputSerializer},
    )
    def get(self, request, pk: int):
        sem = semester_get_selector(id=pk)
        return Response(
            {"success": True, "data": SemesterOutputSerializer(sem).data},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Perbarui Semester",
        request=SemesterUpdateSerializer,
        responses={200: SemesterOutputSerializer},
    )
    def put(self, request, pk: int):
        sem = semester_get_selector(id=pk)
        serializer = SemesterUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_sem = semester_update_service(instance=sem, **serializer.validated_data)
        return Response(
            {
                "success": True,
                "message": "Semester diperbarui.",
                "data": SemesterOutputSerializer(updated_sem).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Hapus Semester",
        responses={200: None},
    )
    def delete(self, request, pk: int):
        sem = semester_get_selector(id=pk)
        semester_delete_service(instance=sem)
        return Response(
            {"success": True, "message": "Semester berhasil dihapus."},
            status=status.HTTP_200_OK,
        )


# ==================== KELAS ====================
@extend_schema(tags=["Kelas"])
class KelasListCreateApi(APIView):
    permission_classes = [IsAdminRole]
    permission_classes = [IsGuruRole]

    class Pagination(LimitOffsetPagination):
        default_limit = 10

    @extend_schema(
        summary="Daftar Kelas",
        responses={200: KelasOutputSerializer(many=True)},
    )
    def get(self, request):
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=KelasOutputSerializer,
            queryset=kelas_list_selector(),
            request=request,
            view=self,
        )

    @extend_schema(
        summary="Buat Kelas Baru",
        request=KelasInputSerializer,
        responses={201: KelasOutputSerializer},
    )
    def post(self, request):
        serializer = KelasInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        kelas = kelas_create_service(**serializer.validated_data)
        return Response(
            {
                "success": True,
                "message": "Kelas berhasil dibuat.",
                "data": KelasOutputSerializer(kelas).data,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Kelas"])
class KelasDetailApi(APIView):
    permission_classes = [IsAdminRole]
    permission_classes = [IsGuruRole]

    @extend_schema(
        summary="Detail Kelas",
        responses={200: KelasOutputSerializer},
    )
    def get(self, request, pk: int):
        kelas = kelas_get_selector(id=pk)
        return Response(
            {"success": True, "data": KelasOutputSerializer(kelas).data},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Perbarui Kelas",
        request=KelasUpdateSerializer,
        responses={200: KelasOutputSerializer},
    )
    def put(self, request, pk: int):
        kelas = kelas_get_selector(id=pk)
        serializer = KelasUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_kelas = kelas_update_service(instance=kelas, **serializer.validated_data)
        return Response(
            {
                "success": True,
                "message": "Kelas diperbarui.",
                "data": KelasOutputSerializer(updated_kelas).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Hapus Kelas",
        responses={200: None},
    )
    def delete(self, request, pk: int):
        kelas = kelas_get_selector(id=pk)
        kelas_delete_service(instance=kelas)
        return Response(
            {"success": True, "message": "Kelas berhasil dihapus."},
            status=status.HTTP_200_OK,
        )


# ==================== MATA PELAJARAN ====================
@extend_schema(tags=["Mata Pelajaran"])
class MataPelajaranListCreateApi(APIView):
    permission_classes = [IsAdminRole]
    permission_classes = [IsGuruRole]

    class Pagination(LimitOffsetPagination):
        default_limit = 10

    @extend_schema(
        summary="Daftar Mata Pelajaran",
        responses={200: MataPelajaranOutputSerializer(many=True)},
    )
    def get(self, request):
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=MataPelajaranOutputSerializer,
            queryset=mapel_list_selector(),
            request=request,
            view=self,
        )

    @extend_schema(
        summary="Buat Mata Pelajaran Baru",
        request=MataPelajaranInputSerializer,
        responses={201: MataPelajaranOutputSerializer},
    )
    def post(self, request):
        serializer = MataPelajaranInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mapel = mapel_create_service(**serializer.validated_data)
        return Response(
            {
                "success": True,
                "message": "Mata pelajaran berhasil dibuat.",
                "data": MataPelajaranOutputSerializer(mapel).data,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Mata Pelajaran"])
class MataPelajaranDetailApi(APIView):
    permission_classes = [IsAdminRole]
    permission_classes = [IsGuruRole]

    @extend_schema(
        summary="Detail Mata Pelajaran",
        responses={200: MataPelajaranOutputSerializer},
    )
    def get(self, request, pk: int):
        mapel = mapel_get_selector(id=pk)
        return Response(
            {"success": True, "data": MataPelajaranOutputSerializer(mapel).data},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Perbarui Mata Pelajaran",
        request=MataPelajaranUpdateSerializer,
        responses={200: MataPelajaranOutputSerializer},
    )
    def put(self, request, pk: int):
        mapel = mapel_get_selector(id=pk)
        serializer = MataPelajaranUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_mapel = mapel_update_service(instance=mapel, **serializer.validated_data)
        return Response(
            {
                "success": True,
                "message": "Mata pelajaran diperbarui.",
                "data": MataPelajaranOutputSerializer(updated_mapel).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Hapus Mata Pelajaran",
        responses={200: None},
    )
    def delete(self, request, pk: int):
        mapel = mapel_get_selector(id=pk)
        mapel_delete_service(instance=mapel)
        return Response(
            {"success": True, "message": "Mata pelajaran berhasil dihapus."},
            status=status.HTTP_200_OK,
        )



# ==================== SISWA ====================
@extend_schema(tags=["Siswa"])
class SiswaListCreateApi(APIView):
    permission_classes = [IsAdminRole]
    permission_classes = [IsGuruRole]

    class Pagination(LimitOffsetPagination):
        default_limit = 10

    @extend_schema(
        summary="Daftar Siswa",
        description="Mengambil daftar siswa terpaginasi dengan opsi pencarian nama/NISN dan filter kelas.",
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Cari berdasarkan Nama atau NISN",
                required=False,
            ),
            OpenApiParameter(
                name="kelas_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter berdasarkan ID Kelas (Kosong = Semua Siswa)",
                required=False,
            ),
        ],
        responses={200: SiswaOutputSerializer(many=True)},
    )
    def get(self, request):
        # 1. Tangkap parameter pencarian (Aman dari None)
        search = request.query_params.get("search", "").strip()
        search = search if search else None

        # 2. Tangkap parameter kelas_id
        kelas_id_raw = request.query_params.get("kelas_id")
        
        # 3. Casting yang absolut aman
        # Akan menjadi None jika frontend mengirim "?kelas_id=", "?kelas_id=null", atau tidak mengirim parameter sama sekali.
        try:
            kelas_id = int(kelas_id_raw)
        except (TypeError, ValueError):
            kelas_id = None

        # 4. Return data
        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=SiswaOutputSerializer,
            queryset=siswa_list_selector(search=search, kelas_id=kelas_id),
            request=request,
            view=self,
        )
    @extend_schema(
        summary="Buat Siswa Baru (Auto Generate Akun)",
        description="Mendaftarkan siswa sekaligus otomatis membuatkan kredensial login (User Siswa & User Orang Tua) berbasis NISN.",
        request=SiswaInputSerializer,
        responses={201: SiswaOutputSerializer},
    )
    def post(self, request):
        serializer = SiswaInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        siswa = siswa_create_service(**serializer.validated_data)
        return Response(
            {
                "success": True,
                "message": "Siswa beserta akun autentikasinya berhasil dibuat.",
                "data": SiswaOutputSerializer(siswa).data,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Siswa"])
class SiswaDetailApi(APIView):
    
    permission_classes = [ IsAdminRole]
    permission_classes = [IsGuruRole] 
   

    @extend_schema(
        summary="Detail Siswa",
        responses={200: SiswaOutputSerializer},
    )
    def get(self, request, nisn: str):
        siswa = siswa_get_selector(nisn=nisn)
        return Response(
            {"success": True, "data": SiswaOutputSerializer(siswa).data},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Perbarui Siswa",
        request=SiswaUpdateSerializer,
        responses={200: SiswaOutputSerializer},
    )
    def put(self, request, nisn: str):
        siswa = siswa_get_selector(nisn=nisn)
        serializer = SiswaUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_siswa = siswa_update_service(instance=siswa, **serializer.validated_data)
        return Response(
            {
                "success": True,
                "message": "Siswa diperbarui.",
                "data": SiswaOutputSerializer(updated_siswa).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Hapus Siswa",
        responses={200: None},
    )
    def delete(self, request, nisn: str):
        siswa = siswa_get_selector(nisn=nisn)
        siswa_delete_service(instance=siswa)
        return Response(
            {"success": True, "message": "Siswa berhasil dihapus."},
            status=status.HTTP_200_OK,
        )