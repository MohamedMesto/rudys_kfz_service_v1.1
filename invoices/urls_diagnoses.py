from django.urls import path
from .views_diagnosis import (
    DiagnosisListView,
    DiagnosisCreateView,
    DiagnosisUpdateView,
    DiagnosisDeleteView,
)

app_name = "diagnoses"

urlpatterns = [
    path("", DiagnosisListView.as_view(), name="list"),
    path("create/", DiagnosisCreateView.as_view(), name="create"),
    path("<int:pk>/update/", DiagnosisUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", DiagnosisDeleteView.as_view(), name="delete"),
]
