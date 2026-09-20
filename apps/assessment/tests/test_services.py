from datetime import date
from django.test import TestCase
from unittest.mock import patch
from rest_framework.exceptions import ValidationError 

from academic.models import TahunAjaran, Semester, Kelas, Siswa, MataPelajaran
from assessment import services
from assessment.models import HistoriStudytime, NilaiSiswa, PresensiSiswa

class AssessmentServicesTest(TestCase):
    def setUp(self):
        self.ta = TahunAjaran.objects.create(nama="2025/2026", is_aktif=True)
        self.semester = Semester.objects.create(
            tahun_ajaran=self.ta,
            semester_ke=1,
            is_aktif=True,
            tanggal_mulai=date(2026, 1, 5),
            tanggal_selesai=date(2026, 6, 30),
        )
        self.kelas = Kelas.objects.create(nama_kelas="10 IPA 1")
        self.siswa = Siswa.objects.create(nisn="0012345678", nama="Budi", gender="L", kelas=self.kelas)
        self.mapel = MataPelajaran.objects.create(kode_mapel="MAT10", nama_mapel="Matematika")

    def test_record_studytime_creates_and_updates(self):
        studytime = services.record_studytime(
            siswa_nisn=self.siswa.nisn,
            mapel_id=self.mapel.id,
            semester_id=self.semester.id,
            minggu_ke=1,
            studytime=5
        )
        self.assertEqual(HistoriStudytime.objects.count(), 1)
        self.assertEqual(studytime.studytime, 5)

        updated = services.record_studytime(
            siswa_nisn=self.siswa.nisn,
            mapel_id=self.mapel.id,
            semester_id=self.semester.id,
            minggu_ke=1,
            studytime=8
        )
        self.assertEqual(HistoriStudytime.objects.count(), 1)
        self.assertEqual(updated.studytime, 8)

    # TANPA MOCK DI SINI KARENA PRESENSI TIDAK MEMAKAI THREAD
    def test_bulk_record_presensi(self):
        items = [
            {
                "siswa_nisn": self.siswa.nisn,
                "presensi_harian": [
                    {"tanggal": date(2026, 1, 12), "status": PresensiSiswa.StatusChoices.HADIR}
                ]
            }
        ]
        records = services.bulk_record_presensi(
            mapel_id=self.mapel.id,
            semester_id=self.semester.id,
            tanggal_mulai=date(2026, 1, 10),
            tanggal_akhir=date(2026, 1, 15),
            items=items
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].status, PresensiSiswa.StatusChoices.HADIR)
        self.assertEqual(records[0].tanggal, date(2026, 1, 12))

    # DUA MOCK DENGAN DUA ARGUMEN
    @patch('assessment.services.transaction.on_commit', side_effect=lambda hook: hook())
    @patch('assessment.services.threading.Thread')
    def test_bulk_record_assessment(self, mock_thread, mock_on_commit):
        items = [
            {
                "siswa_nisn": self.siswa.nisn,
                "studytime": 10,
                "evaluasi_list": [
                    {
                        "jenis_evaluasi": NilaiSiswa.EvaluasiChoices.QUIZ,
                        "nama_evaluasi": "Quiz 1",
                        "skor": 85.5
                    }
                ]
            }
        ]
        
        result = services.bulk_record_assessment(
            mapel_id=self.mapel.id,
            semester_id=self.semester.id,
            tanggal_input=date(2026, 1, 15),
            items=items
        )
        
        self.assertEqual(len(result["studytime_records"]), 1)
        self.assertEqual(len(result["nilai_records"]), 1)
        self.assertEqual(HistoriStudytime.objects.first().studytime, 10)
        self.assertEqual(NilaiSiswa.objects.first().skor, 85.5)
        self.assertTrue(mock_thread.called)

    def test_validation_errors(self):
        with self.assertRaises(ValidationError):
            services.record_studytime(
                siswa_nisn=self.siswa.nisn,
                mapel_id=999,
                semester_id=self.semester.id,
                minggu_ke=1,
                studytime=5
            )

        with self.assertRaises(ValidationError):
            services.bulk_record_assessment(
                mapel_id=self.mapel.id,
                semester_id=self.semester.id,
                tanggal_input=date(2026, 1, 15),
                items=[{"siswa_nisn": "999999", "studytime": 2, "evaluasi_list": []}]
            )