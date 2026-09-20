import random
from datetime import date, timedelta
from faker import Faker
from django.core.management.base import BaseCommand
from authentication.models import User
from academic.models import TahunAjaran, Semester, Kelas, MataPelajaran, Siswa
from assessment.models import (
    HistoriStudytime, 
    NilaiSiswa, 
    PresensiSiswa, 
    PredictionResult
)

class Command(BaseCommand):
    help = "Generate data dummy 100 siswa, akun user, dan relasi assessment minggu 1-4 (Lengkap untuk ML)"

    def handle(self, *args, **kwargs):
        fake = Faker('id_ID')

        self.stdout.write("Membersihkan data dummy lama...")
        PredictionResult.objects.all().delete()
        NilaiSiswa.objects.all().delete()
        PresensiSiswa.objects.all().delete()
        HistoriStudytime.objects.all().delete()
        Siswa.objects.all().delete()
        User.objects.filter(role__in=[User.Role.GURU, User.Role.SISWA, User.Role.ORANGTUA]).delete()

        self.stdout.write("Memulai pembuatan data dummy...")

        # 1. Setup Tahun Ajaran & Semester Active
        base_date = date(2026, 8, 3)  # Tanggal patokan Senin Minggu ke-1
        ta, _ = TahunAjaran.objects.get_or_create(nama="2025/2026", defaults={"is_aktif": True})
        semester, _ = Semester.objects.get_or_create(
            tahun_ajaran=ta, 
            semester_ke=Semester.SemesterChoices.GANJIL, 
            defaults={
                "is_aktif": True,
                "tanggal_mulai": base_date,
                "tanggal_selesai": base_date + timedelta(weeks=20)
            }
        )

        # 2. Setup Guru Pengajar & Wali Kelas
        guru_list = []
        guru_names = ["Budi Santoso", "Siti Aminah", "Eko Prasetyo", "Dewi Lestari", "Rahmat Hidayat"]
        for idx, name in enumerate(guru_names, 1):
            guru, _ = User.objects.get_or_create(
                email=f"guru{idx}@school.id",
                defaults={
                    "role": User.Role.GURU,
                    "first_name": name.split()[0],
                    "last_name": name.split()[-1]
                }
            )
            guru.set_password("password123")
            guru.save()
            guru_list.append(guru)

        # 3. Setup Mata Pelajaran & Assign Pengajar
        mapel_data = [
            ("MATH10", "Matematika", guru_list[0]),
            ("IND10", "Bahasa Indonesia", guru_list[1]),
            ("ENG10", "Bahasa Inggris", guru_list[2]),
            ("PHY10", "Fisika", guru_list[3]),
            ("ECO10", "Ekonomi", guru_list[4])
        ]
        mapel_list = []
        for kode, nama, pengajar in mapel_data:
            m, _ = MataPelajaran.objects.get_or_create(
                kode_mapel=kode, 
                defaults={"nama_mapel": nama, "pengajar": pengajar}
            )
            mapel_list.append(m)

        # 4. Distribusi Kelas & Siswa (Total 100 Siswa)
        distribusi_kelas = [
            {"tingkat": "X", "jurusan": "IPA", "jumlah": 20},
            {"tingkat": "X", "jurusan": "IPS", "jumlah": 15},
            {"tingkat": "XI", "jurusan": "IPA", "jumlah": 25},
            {"tingkat": "XI", "jurusan": "IPS", "jumlah": 10},
            {"tingkat": "XII", "jurusan": "IPA", "jumlah": 18},
            {"tingkat": "XII", "jurusan": "IPS", "jumlah": 12},
        ]

        nisn_counter = 1000000000

        # Parameter Evaluasi Wajib Per Minggu untuk Input ML
        evaluasi_wajib = [
            (NilaiSiswa.EvaluasiChoices.QUIZ, "Quiz 1"),
            (NilaiSiswa.EvaluasiChoices.QUIZ2, "Quiz 2"),
            (NilaiSiswa.EvaluasiChoices.TUGAS, "Tugas Utama"),
        ]

        for idx, dist in enumerate(distribusi_kelas):
            nama_kelas = f"{dist['tingkat']} {dist['jurusan']} 1"
            wali_kelas_guru = guru_list[idx % len(guru_list)]
            kelas_obj, _ = Kelas.objects.get_or_create(
                nama_kelas=nama_kelas, 
                defaults={"wali_kelas": wali_kelas_guru}
            )

            for _ in range(dist['jumlah']):
                nisn_counter += 1
                nisn_str = str(nisn_counter)
                gender = random.choice(['L', 'P'])
                nama_siswa = fake.name()

                # A. Buat Akun User Orang Tua & Siswa
                ortu_user = User.objects.create_user(
                    email=f"ortu_{nisn_str}@school.id",
                    password="password123",
                    role=User.Role.ORANGTUA,
                    first_name="Orang Tua dari",
                    last_name=nama_siswa
                )

                User.objects.create_user(
                    email=f"siswa_{nisn_str}@school.id",
                    password="password123",
                    role=User.Role.SISWA,
                    first_name=nama_siswa.split()[0],
                    last_name=nama_siswa.split()[-1] if len(nama_siswa.split()) > 1 else ""
                )

                # B. Buat Entity Siswa
                siswa = Siswa.objects.create(
                    nisn=nisn_str,
                    nama=nama_siswa,
                    gender=gender,
                    kelas=kelas_obj,
                    parent_user=ortu_user
                )

                # C. Loop Transaksi Assessment Minggu 1 - 4
                for minggu in range(1, 5):
                    tanggal_presensi = base_date + timedelta(weeks=minggu - 1)

                    for mapel in mapel_list:
                        # 1. Histori Studytime (Jam Belajar)
                        HistoriStudytime.objects.create(
                            siswa=siswa,
                            mapel=mapel,
                            semester=semester,
                            minggu_ke=minggu,
                            studytime=random.randint(1, 8)
                        )

                        # 2. Nilai Siswa (WAJIB: Quiz 1, Quiz 2, & Tugas di setiap minggu)
                        for jenis_eval, label_eval in evaluasi_wajib:
                            NilaiSiswa.objects.create(
                                siswa=siswa,
                                mapel=mapel,
                                semester=semester,
                                minggu_ke=minggu,
                                jenis_evaluasi=jenis_eval,
                                nama_evaluasi=f"{label_eval} M{minggu}",
                                skor=round(random.uniform(55.0, 98.0), 1),
                                is_terlambat=random.choices([False, True], weights=[85, 15])[0]
                            )

                        # Tambahan UTS khusus pada Minggu ke-4 jika diperlukan
                        if minggu == 4:
                            NilaiSiswa.objects.create(
                                siswa=siswa,
                                mapel=mapel,
                                semester=semester,
                                minggu_ke=minggu,
                                jenis_evaluasi=NilaiSiswa.EvaluasiChoices.UTS,
                                nama_evaluasi="UTS Semester Ganjil",
                                skor=round(random.uniform(60.0, 98.0), 1),
                                is_terlambat=False
                            )

                        # 3. Presensi Siswa
                        PresensiSiswa.objects.create(
                            siswa=siswa,
                            mapel=mapel,
                            semester=semester,
                            minggu_ke=minggu,
                            tanggal=tanggal_presensi,
                            status=random.choices(["Hadir", "Izin", "Sakit", "Alpa"], weights=[80, 10, 5, 5])[0]
                        )

                        # 4. Prediction Result (JSON Rekomendasi Multi-Role)
                        risk = random.choices([
                            PredictionResult.RiskChoices.LOW, 
                            PredictionResult.RiskChoices.MEDIUM, 
                            PredictionResult.RiskChoices.HIGH
                        ], weights=[70, 20, 10])[0]

                        rec_json = {
                            "guru": "Berikan latihan interaktif tambahan." if risk != 0 else "Pertahankan ritme mengajar saat ini.",
                            "orangtua": "Pantau jadwal belajar mandiri anak di rumah." if risk != 0 else "Apresiasi pencapaian belajar anak.",
                            "siswa": "Tingkatkan frekuensi latihan soal mingguan." if risk != 0 else "Pertahankan kebiasaan belajar yang baik."
                        }

                        PredictionResult.objects.create(
                            siswa=siswa,
                            mapel=mapel,
                            semester=semester,
                            minggu_ke=minggu,
                            risk_score=risk,
                            recommendation=rec_json
                        )

        self.stdout.write(self.style.SUCCESS("Berhasil generate 100 siswa dengan parameter ML lengkap per minggu!"))