from django.urls import path
from .views import (
    KelasDetailApi,
    KelasListCreateApi,
    MataPelajaranDetailApi,
    MataPelajaranListCreateApi,
    SemesterDetailApi,
    SemesterListCreateApi,
    SiswaDetailApi,
    SiswaListCreateApi,

    TahunAjaranDetailApi,
    TahunAjaranListCreateApi,
)

app_name = "academic"

urlpatterns = [
    # Tahun Ajaran
    path("tahun-ajaran/", TahunAjaranListCreateApi.as_view(), name="tahun_ajaran_list_create"),
    path("tahun-ajaran/<int:pk>/", TahunAjaranDetailApi.as_view(), name="tahun_ajaran_detail"),
    # Semester
    path("semester/", SemesterListCreateApi.as_view(), name="semester_list_create"),
    path("semester/<int:pk>/", SemesterDetailApi.as_view(), name="semester_detail"),
    # Kelas
    path("kelas/", KelasListCreateApi.as_view(), name="kelas_list_create"),
    path("kelas/<int:pk>/", KelasDetailApi.as_view(), name="kelas_detail"),
    # Mapel
    path("mapel/", MataPelajaranListCreateApi.as_view(), name="mapel_list_create"),
    path("mapel/<int:pk>/", MataPelajaranDetailApi.as_view(), name="mapel_detail"),
    # Siswa
    path("siswa/", SiswaListCreateApi.as_view(), name="siswa_list_create"),
    path("siswa/<str:nisn>/", SiswaDetailApi.as_view(), name="siswa_detail"),

]