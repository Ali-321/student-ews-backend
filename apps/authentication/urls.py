
from django.urls import path
from .views import LoginApi, MeApi, TokenRefreshApi

urlpatterns = [
    path("login/", LoginApi.as_view(), name="login"),
    path("refresh/", TokenRefreshApi.as_view(), name="token_refresh"),
    path("me/", MeApi.as_view(), name="me"),
]