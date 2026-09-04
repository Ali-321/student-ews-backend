from django.urls import path
from .views import DashboardSummaryView, DashboardAnalyticsView

app_name = "dashboard"

urlpatterns = [
    path('summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('analytics/', DashboardAnalyticsView.as_view(), name='dashboard-analytics'),
]