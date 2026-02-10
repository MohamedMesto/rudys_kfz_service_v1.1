# invoices/urls_auth.py
from django.urls import path
from .views_auth import register_view, login_view, logout_view, profile_view

app_name = "auth"

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
]
