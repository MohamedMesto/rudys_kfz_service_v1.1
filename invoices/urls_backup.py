from django.urls import path
from .views_backup import (
    backup_dashboard_view,
    create_backup_view,
    download_backup_view,
)

app_name = "backup"

urlpatterns = [
    path("", backup_dashboard_view, name="dashboard"),
    path("create/", create_backup_view, name="create"),
    path("download/<str:filename>/", download_backup_view, name="download"),
]