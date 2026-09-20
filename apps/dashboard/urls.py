from django.urls import path

from .views import DashboardOrangTuaView, DashboardSummaryView, DashboardAnalyticsView, DashboardSiswaView

app_name = "dashboard"

urlpatterns = [
    path('summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('analytics/', DashboardAnalyticsView.as_view(), name='dashboard-analytics'),
    path('student/<str:siswa_nisn>/', DashboardSiswaView.as_view(), name='dashboard-student'),
    path('parent/<str:siswa_nisn>/', DashboardOrangTuaView.as_view(), name='dashboard-parent')
]