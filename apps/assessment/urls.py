from django.urls import path
from assessment import views

app_name = "assessment"

urlpatterns = [
    path(
        "studytime/",
        views.HistoriStudytimeListCreateAPIView.as_view(),
        name="studytime-list-create",
    ),
    path(
        "nilai/",
        views.NilaiSiswaListCreateAPIView.as_view(),
        name="nilai-list-create",
    ),
    path(
        "presensi/",
        views.PresensiBulkCreateAPIView.as_view(),
        name="presensi-list-bulk-create",
    ),
    path(
        "predictions/",
        views.PredictionResultListCreateAPIView.as_view(),
        name="prediction-list-create",
    ),
    path(
        "ringkasan-akademik/<str:siswa_nisn>/",
        views.RingkasanAkademikSiswaAPIView.as_view(),
        name="siswa-ringkasan-akademik",
    ),
]