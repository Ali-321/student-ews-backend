from django.db.models import QuerySet
from rest_framework.exceptions import NotFound

from academic.models import Kelas, MataPelajaran, Semester, Siswa, TahunAjaran


# --- TAHUN AJARAN ---
def tahun_ajaran_list_selector() -> QuerySet[TahunAjaran]:
    return TahunAjaran.objects.all().order_by("-id")


def tahun_ajaran_get_selector(*, id: int) -> TahunAjaran:
    instance = TahunAjaran.objects.filter(id=id).first()
    if not instance:
        raise NotFound("Tahun Ajaran tidak ditemukan.")
    return instance


# --- SEMESTER ---
def semester_list_selector(*, tahun_ajaran_id: int = None) -> QuerySet[Semester]:
    qs = Semester.objects.select_related("tahun_ajaran").all().order_by("-id")
    if tahun_ajaran_id:
        qs = qs.filter(tahun_ajaran_id=tahun_ajaran_id)
    return qs


def semester_get_selector(*, id: int) -> Semester:
    instance = Semester.objects.select_related("tahun_ajaran").filter(id=id).first()
    if not instance:
        raise NotFound("Semester tidak ditemukan.")
    return instance


# --- KELAS ---
def kelas_list_selector() -> QuerySet[Kelas]:
    return Kelas.objects.select_related("wali_kelas").all().order_by("nama_kelas")


def kelas_get_selector(*, id: int) -> Kelas:
    instance = Kelas.objects.select_related("wali_kelas").filter(id=id).first()
    if not instance:
        raise NotFound("Kelas tidak ditemukan.")
    return instance


# --- MATA PELAJARAN ---
def mapel_list_selector() -> QuerySet[MataPelajaran]:
    return MataPelajaran.objects.select_related("pengajar").all().order_by("kode_mapel")


def mapel_get_selector(*, id: int) -> MataPelajaran:
    instance = MataPelajaran.objects.select_related("pengajar").filter(id=id).first()
    if not instance:
        raise NotFound("Mata Pelajaran tidak ditemukan.")
    return instance


# --- SISWA ---
def siswa_list_selector(*, kelas_id: int = None) -> QuerySet[Siswa]:
    qs = Siswa.objects.select_related("kelas", "parent_user").all().order_by("nama")
    if kelas_id:
        qs = qs.filter(kelas_id=kelas_id)


def siswa_get_selector(*, nisn: str) -> Siswa:
    instance = Siswa.objects.select_related("kelas", "parent_user").filter(nisn=nisn).first()
    if not instance:
        raise NotFound("Siswa tidak ditemukan.")
    return instance