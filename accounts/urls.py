"""Defines URL patterns for accounts."""

from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import CustomLoginView

app_name = "accounts"

urlpatterns = [
    # Include default authentication URLs (password reset, etc.)
    path("", include("django.contrib.auth.urls")),

    # Override the default login view with your custom one
    path("login/", CustomLoginView.as_view(), name="login"),

    # Custom logout view (optional, but keeps it explicit)
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
