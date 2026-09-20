from django.urls import path
from assessment import views

app_name = "assessment"

urlpatterns = [
    # --- Study Time ---
    path(
        "studytime/",
        views.HistoriStudytimeListCreateAPIView.as_view(),
        name="studytime-list-create",
    ),
    # --- Nilai ---
    path(
        "nilai/",
        views.NilaiSiswaListCreateAPIView.as_view(),
        name="nilai-list-create",
    ),
    # --- Presensi ---
    path(
        "presensi/",
        views.PresensiBulkCreateAPIView.as_view(),
        name="presensi-list-bulk-create",
    ),
    path(
        "presensi/status-choices/",
        views.StatusChoicesAPIView.as_view(),
        name="presensi-status-choices",
    ),
    # --- Risk Analytics / EWS ---
    path(
        "siswa-risk-summary/",
        views.SiswaRiskSummaryListApi.as_view(),
        name="siswa-risk-summary",
    ),
    path(
        "detail-prediksi/<str:siswa_nisn>/<int:mapel_id>/<int:minggu_ke>/",
        views.DetailPrediksiEWSApi.as_view(),
        name="detail-prediksi-ews",
    ),
    path(
        "detail-siswa/<str:siswa_nisn>/",
        views.DetailProfilSiswaEWSApi.as_view(),
        name="detail-siswa-ews",
    ),
]