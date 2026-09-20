import threading
from django.db import transaction, connection
from rest_framework.exceptions import ValidationError

from academic.models import Siswa, MataPelajaran, Semester
from assessment.ai_pipeline import process_batch_ews_pipeline
from assessment.models import HistoriStudytime, NilaiSiswa, PresensiSiswa

# ==========================================
# WORKER THREAD UNTUK EWS PIPELINE (BATCH)
# ==========================================
def run_pipeline_in_background(nisn_list: list, mapel_id: int, semester_id: int, minggu_ke: int):
    """
    Eksekusi AI Pipeline (Batch) secara paralel di background.
    PENTING: Blok 'finally' digunakan untuk mencegah database connection leak.
    """
    try:
        # Panggil versi BATCH satu kali saja, bukan me-looping function
        process_batch_ews_pipeline(
            list_nisn=nisn_list,
            mapel_id=mapel_id,
            semester_id=semester_id,
            minggu_ke=minggu_ke
        )
    except Exception as e:
        print(f"Error Pipeline Batch Background: {e}")
    finally:
        # Menutup koneksi database setelah thread buatan selesai bekerja
        connection.close()


# ==========================================
# SERVICES
# ==========================================
@transaction.atomic
def record_studytime(
    *,
    siswa_nisn: str,
    mapel_id: int,
    semester_id: int,
    minggu_ke: int,
    studytime: int
) -> HistoriStudytime:
    siswa = Siswa.objects.filter(nisn=siswa_nisn).first()
    if not siswa: raise ValidationError({"siswa_nisn": f"Siswa dengan NISN {siswa_nisn} tidak ditemukan."})
    
    mapel = MataPelajaran.objects.filter(pk=mapel_id).first()
    if not mapel: raise ValidationError({"mapel_id": f"Mata pelajaran dengan ID {mapel_id} tidak ditemukan."})
    
    semester = Semester.objects.filter(pk=semester_id).first()
    if not semester: raise ValidationError({"semester_id": f"Semester dengan ID {semester_id} tidak ditemukan."})

    obj, created = HistoriStudytime.objects.update_or_create(
        siswa=siswa,
        mapel=mapel,
        semester=semester,
        minggu_ke=minggu_ke,
        defaults={"studytime": studytime}
    )
    return obj


@transaction.atomic
def bulk_record_presensi(*, mapel_id: int, semester_id: int, tanggal_mulai, tanggal_akhir, items: list) -> list[PresensiSiswa]:
    semester = Semester.objects.filter(id=semester_id).first()
    if not semester:
        raise ValidationError({"semester_id": f"Semester dengan ID {semester_id} tidak ditemukan."})

    mapel = MataPelajaran.objects.filter(id=mapel_id).first()
    if not mapel:
        raise ValidationError({"mapel_id": f"Mata pelajaran dengan ID {mapel_id} tidak ditemukan."})

    presensi_records = []
    for student_item in items:
        nisn = student_item["siswa_nisn"]
        siswa = Siswa.objects.filter(nisn=nisn).first()
        if not siswa:
            raise ValidationError({"siswa_nisn": f"Siswa dengan NISN {nisn} tidak ditemukan di database."})
        
        for harian in student_item["presensi_harian"]:
            tgl = harian["tanggal"]
            minggu_ke = semester.get_minggu_ke(target_date=tgl)

            presensi, _ = PresensiSiswa.objects.update_or_create(
                siswa=siswa,
                mapel=mapel,
                semester=semester,
                tanggal=tgl,
                defaults={
                    "minggu_ke": minggu_ke,
                    "status": harian["status"],
                }
            )
            presensi_records.append(presensi)

    return presensi_records


@transaction.atomic
def bulk_record_assessment(*, mapel_id: int, semester_id: int, tanggal_input, items: list) -> dict:
    semester = Semester.objects.filter(id=semester_id).first()
    if not semester:
        raise ValidationError({"semester_id": f"Semester dengan ID {semester_id} tidak ditemukan."})
        
    mapel = MataPelajaran.objects.filter(id=mapel_id).first()
    if not mapel:
        raise ValidationError({"mapel_id": f"Mata pelajaran dengan ID {mapel_id} tidak ditemukan."})
    
    # Hitung minggu_ke otomatis dari tanggal_input menggunakan method di model Semester
    calculated_minggu_ke = semester.get_minggu_ke(target_date=tanggal_input)

    nilai_records = []
    studytime_records = []
    processed_nisn_list = []

    for student_item in items:
        nisn = student_item["siswa_nisn"]
        siswa = Siswa.objects.filter(nisn=nisn).first()
        if not siswa:
            raise ValidationError({"siswa_nisn": f"Siswa dengan NISN {nisn} tidak ditemukan di database."})
            
        processed_nisn_list.append(siswa.nisn)

        # 1. Upsert Study Time jika diisi
        if student_item.get("studytime") is not None:
            st, _ = HistoriStudytime.objects.update_or_create(
                siswa=siswa,
                mapel=mapel,
                semester=semester,
                minggu_ke=calculated_minggu_ke,
                defaults={"studytime": student_item["studytime"]}
            )
            studytime_records.append(st)

        # 2. Upsert Nilai Evaluasi (Quiz 1, Tugas, Quiz 2, dll)
        for eval_item in student_item.get("evaluasi_list", []):
            if eval_item.get("skor") is not None:
                nilai, _ = NilaiSiswa.objects.update_or_create(
                    siswa=siswa,
                    mapel=mapel,
                    semester=semester,
                    jenis_evaluasi=eval_item["jenis_evaluasi"],
                    nama_evaluasi=eval_item["nama_evaluasi"],
                    defaults={
                        "minggu_ke": calculated_minggu_ke,
                        "skor": eval_item["skor"],
                    }
                )
                nilai_records.append(nilai)

    # Kumpulkan NISN unik untuk diproses ML & LLM
    unique_nisn_list = list(set(processed_nisn_list))

    # ==========================================
    # TRIGGER EWS PIPELINE DI BACKGROUND
    # ==========================================
    def trigger_background_ai():
        thread = threading.Thread(
            target=run_pipeline_in_background,
            args=(unique_nisn_list, mapel_id, semester_id, calculated_minggu_ke)
        )
        thread.start()

    # Memastikan AI hanya berjalan SETELAH database di-commit permanen
    transaction.on_commit(trigger_background_ai)

    return {
        "studytime_records": studytime_records,
        "nilai_records": nilai_records,
    }