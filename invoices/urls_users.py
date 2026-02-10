# invoices/urls_users.py
from django.urls import path
from .views_users import user_create_view

app_name = "users"

urlpatterns = [
    path("create/", user_create_view, name="create"),
]
