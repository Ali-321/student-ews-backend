from datetime import date


def calculate_academic_week(start_date: date, target_date: date) -> int:
    """
    Menghitung selisih minggu antara start_date dan target_date.
    Jika target_date terjadi sebelum start_date, default dikembalikan ke minggu ke-1.
    """
    if target_date < start_date:
        return 1

    delta_days = (target_date - start_date).days
    return (delta_days // 7) + 1