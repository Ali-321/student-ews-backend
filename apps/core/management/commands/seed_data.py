import random
from datetime import date, timedelta
from faker import Faker
from django.core.management.base import BaseCommand
from academic.models import TahunAjaran, Semester, Kelas, MataPelajaran, Siswa
from assessment.models import (
    HistoriStudytime, 
    NilaiSiswa, 
    PresensiSiswa, 
    PredictionResult
)

class Command(BaseCommand):
    help = "Generate data dummy 100 siswa dan relasi assessment minggu 1-4"

    def handle(self, *args, **kwargs):
        fake = Faker('id_ID')
        # Hapus data siswa lama agar NISN tidak duplikat
        self.stdout.write("Membersihkan data dummy lama...")
        Siswa.objects.all().delete()

        self.stdout.write("Memulai pembuatan data dummy...")

        # 1. Setup Tahun Ajaran & Semester Active
        ta, _ = TahunAjaran.objects.get_or_create(nama="2025/2026", defaults={"is_aktif": True})
        semester, _ = Semester.objects.get_or_create(tahun_ajaran=ta, semester_ke=1, defaults={"is_aktif": True})

        # 2. Setup Mata Pelajaran
        mapel_data = [
            ("MATH10", "Matematika"),
            ("IND10", "Bahasa Indonesia"),
            ("ENG10", "Bahasa Inggris"),
            ("PHY10", "Fisika"),
            ("ECO10", "Ekonomi")
        ]
        mapel_list = []
        for kode, nama in mapel_data:
            m, _ = MataPelajaran.objects.get_or_create(kode_mapel=kode, defaults={"nama_mapel": nama})
            mapel_list.append(m)

        # 3. Distribusi Siswa Sesuai Kebutuhan (Total 100 Siswa)
        distribusi_kelas = [
            {"tingkat": "X", "jurusan": "IPA", "jumlah": 20, "angkatan": 2026},
            {"tingkat": "X", "jurusan": "IPS", "jumlah": 15, "angkatan": 2026},
            {"tingkat": "XI", "jurusan": "IPA", "jumlah": 25, "angkatan": 2025},
            {"tingkat": "XI", "jurusan": "IPS", "jumlah": 10, "angkatan": 2025},
            {"tingkat": "XII", "jurusan": "IPA", "jumlah": 18, "angkatan": 2024},
            {"tingkat": "XII", "jurusan": "IPS", "jumlah": 12, "angkatan": 2024},
        ]

        nisn_counter = 1000000000
        base_date = date(2026, 8, 3) # Tanggal patokan Senin Minggu ke-1

        for dist in distribusi_kelas:
            nama_kelas = f"{dist['tingkat']} {dist['jurusan']} 1"
            kelas_obj, _ = Kelas.objects.get_or_create(nama_kelas=nama_kelas)

            for _ in range(dist['jumlah']):
                nisn_counter += 1
                nisn_str = str(nisn_counter)
                gender = random.choice(['L', 'P'])

                siswa = Siswa.objects.create(
                    nisn=nisn_str,
                    nama=fake.name(),
                    gender=gender,
                    angkatan=dist['angkatan'],
                    kelas=kelas_obj
                )

                # Loop Data Transaksi per Minggu (Minggu 1 - 4)
                for minggu in range(1, 5):
                    # Tanggal presensi dinamis bertambah 7 hari per minggu
                    tanggal_presensi = base_date + timedelta(weeks=minggu - 1)

                    for mapel in mapel_list:
                        # 1. HistoriStudytime
                        HistoriStudytime.objects.create(
                            siswa=siswa,
                            mapel=mapel,
                            semester=semester,
                            minggu_ke=minggu,
                            studytime=random.randint(1, 8)
                        )

                        # 2. NilaiSiswa
                        NilaiSiswa.objects.create(
                            siswa=siswa,
                            mapel=mapel,
                            semester=semester,
                            minggu_ke=minggu,
                            jenis_evaluasi=NilaiSiswa.EvaluasiChoices.QUIZ,
                            nama_evaluasi=f"Quiz {minggu}",
                            skor=round(random.uniform(50.0, 98.0), 1),
                            is_terlambat=random.choices([False, True], weights=[85, 15])[0]
                        )

                        # 3. PresensiSiswa (Menambahkan tanggal & status sesuai Title Case)
                        PresensiSiswa.objects.create(
                            siswa=siswa,
                            mapel=mapel,
                            semester=semester,
                            minggu_ke=minggu,
                            tanggal=tanggal_presensi,
                            status=random.choices(["Hadir", "Izin", "Sakit", "Alpa"], weights=[80, 10, 5, 5])[0]
                        )

                    # 4. PredictionResult (risk_score menggunakan integer 0, 1, atau 2)
                    risk = random.choices([
                        PredictionResult.RiskChoices.LOW, 
                        PredictionResult.RiskChoices.MEDIUM, 
                        PredictionResult.RiskChoices.HIGH
                    ], weights=[75, 18, 7])[0]

                    PredictionResult.objects.create(
                        siswa=siswa,
                        mapel=mapel_list[0],
                        semester=semester,
                        minggu_ke=minggu,
                        risk_score=risk,
                        recommendation="Perlu pendampingan khusus" if risk != 0 else "Performa baik"
                    )

        self.stdout.write(self.style.SUCCESS("Berhasil generate 100 siswa & relasi assessment minggu 1-4!"))