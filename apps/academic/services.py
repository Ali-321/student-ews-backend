from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError

from academic.models import Kelas, MataPelajaran, Semester, Siswa, TahunAjaran
from authentication.models import User


# --- TAHUN AJARAN ---
@transaction.atomic
def tahun_ajaran_create_service(*, nama: str, is_aktif: bool = False) -> TahunAjaran:
    if is_aktif:
        TahunAjaran.objects.filter(is_aktif=True).update(is_aktif=False)
    return TahunAjaran.objects.create(nama=nama, is_aktif=is_aktif)


@transaction.atomic
def tahun_ajaran_update_service(*, instance: TahunAjaran, **data) -> TahunAjaran:
    if data.get("is_aktif"):
        TahunAjaran.objects.filter(is_aktif=True).exclude(id=instance.id).update(is_aktif=False)

    for field, value in data.items():
        setattr(instance, field, value)

    instance.save()
    return instance


def tahun_ajaran_delete_service(*, instance: TahunAjaran) -> None:
    instance.delete()


# --- SEMESTER ---
@transaction.atomic
def semester_create_service(*, tahun_ajaran_id: int, semester_ke: int, is_aktif: bool = False) -> Semester:
    tahun_ajaran = TahunAjaran.objects.filter(id=tahun_ajaran_id).first()
    if not tahun_ajaran:
        raise ValidationError({"tahun_ajaran_id": "Tahun Ajaran tidak ditemukan."})

    if is_aktif:
        Semester.objects.filter(is_aktif=True).update(is_aktif=False)

    return Semester.objects.create(tahun_ajaran=tahun_ajaran, semester_ke=semester_ke, is_aktif=is_aktif)


@transaction.atomic
def semester_update_service(*, instance: Semester, **data) -> Semester:
    if "tahun_ajaran_id" in data:
        tahun_ajaran = TahunAjaran.objects.filter(id=data.pop("tahun_ajaran_id")).first()
        if not tahun_ajaran:
            raise ValidationError({"tahun_ajaran_id": "Tahun Ajaran tidak ditemukan."})
        instance.tahun_ajaran = tahun_ajaran

    if data.get("is_aktif"):
        Semester.objects.filter(is_aktif=True).exclude(id=instance.id).update(is_aktif=False)

    for field, value in data.items():
        setattr(instance, field, value)

    instance.save()
    return instance


def semester_delete_service(*, instance: Semester) -> None:
    instance.delete()


# --- KELAS ---
def kelas_create_service(*, nama_kelas: str, wali_kelas_id: int = None) -> Kelas:
    wali_kelas = None
    if wali_kelas_id:
        wali_kelas = User.objects.filter(id=wali_kelas_id, role=User.Role.GURU).first()
        if not wali_kelas:
            raise ValidationError({"wali_kelas_id": "User Guru tidak ditemukan."})

    return Kelas.objects.create(nama_kelas=nama_kelas, wali_kelas=wali_kelas)


def kelas_update_service(*, instance: Kelas, **data) -> Kelas:
    if "wali_kelas_id" in data:
        wali_kelas_id = data.pop("wali_kelas_id")
        if wali_kelas_id is None:
            instance.wali_kelas = None
        else:
            wali_kelas = User.objects.filter(id=wali_kelas_id, role=User.Role.GURU).first()
            if not wali_kelas:
                raise ValidationError({"wali_kelas_id": "User Guru tidak ditemukan."})
            instance.wali_kelas = wali_kelas

    for field, value in data.items():
        setattr(instance, field, value)

    instance.save()
    return instance


def kelas_delete_service(*, instance: Kelas) -> None:
    instance.delete()


# --- MATA PELAJARAN ---
def mapel_create_service(*, kode_mapel: str, nama_mapel: str, pengajar_id: int = None) -> MataPelajaran:
    if MataPelajaran.objects.filter(kode_mapel=kode_mapel).exists():
        raise ValidationError({"kode_mapel": "Kode mata pelajaran sudah ada."})

    pengajar = None
    if pengajar_id:
        pengajar = User.objects.filter(id=pengajar_id, role=User.Role.GURU).first()
        if not pengajar:
            raise ValidationError({"pengajar_id": "User Guru tidak ditemukan."})

    return MataPelajaran.objects.create(kode_mapel=kode_mapel, nama_mapel=nama_mapel, pengajar=pengajar)


def mapel_update_service(*, instance: MataPelajaran, **data) -> MataPelajaran:
    if "kode_mapel" in data and data["kode_mapel"] != instance.kode_mapel:
        if MataPelajaran.objects.filter(kode_mapel=data["kode_mapel"]).exists():
            raise ValidationError({"kode_mapel": "Kode mata pelajaran sudah digunakan."})

    if "pengajar_id" in data:
        pengajar_id = data.pop("pengajar_id")
        if pengajar_id is None:
            instance.pengajar = None
        else:
            pengajar = User.objects.filter(id=pengajar_id, role=User.Role.GURU).first()
            if not pengajar:
                raise ValidationError({"pengajar_id": "User Guru tidak ditemukan."})
            instance.pengajar = pengajar

    for field, value in data.items():
        setattr(instance, field, value)

    instance.save()
    return instance


def mapel_delete_service(*, instance: MataPelajaran) -> None:
    instance.delete()


# --- SISWA ---
def siswa_create_service(
    *,
    nisn: str,
    nama: str,
    gender: str,
    kelas_id: int,
    parent_user_id: int = None,
) -> Siswa:
    if Siswa.objects.filter(nisn=nisn).exists():
        raise ValidationError({"nisn": "Siswa dengan NISN ini sudah terdaftar."})

    kelas = Kelas.objects.filter(id=kelas_id).first()
    if not kelas:
        raise ValidationError({"kelas_id": "Kelas tidak ditemukan."})

    parent_user = None
    if parent_user_id:
        parent_user = User.objects.filter(id=parent_user_id, role=User.Role.ORANGTUA).first()
        if not parent_user:
            raise ValidationError({"parent_user_id": "User Orang Tua tidak ditemukan."})

    return Siswa.objects.create(
        nisn=nisn,
        nama=nama,
        gender=gender,
        kelas=kelas,
        parent_user=parent_user,
    )


def siswa_update_service(*, instance: Siswa, **data) -> Siswa:
    if "kelas_id" in data:
        kelas = Kelas.objects.filter(id=data.pop("kelas_id")).first()
        if not kelas:
            raise ValidationError({"kelas_id": "Kelas tidak ditemukan."})
        instance.kelas = kelas

    if "parent_user_id" in data:
        parent_user_id = data.pop("parent_user_id")
        if parent_user_id is None:
            instance.parent_user = None
        else:
            parent_user = User.objects.filter(id=parent_user_id, role=User.Role.ORANGTUA).first()
            if not parent_user:
                raise ValidationError({"parent_user_id": "User Orang Tua tidak ditemukan."})
            instance.parent_user = parent_user

    for field, value in data.items():
        setattr(instance, field, value)

    instance.save()
    return instance


def siswa_delete_service(*, instance: Siswa) -> None:
    instance.delete()