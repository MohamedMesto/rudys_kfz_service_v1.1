from django.urls import path
from .views_companies import (
    CompanyListView,
    CompanyCreateView,
    CompanyUpdateView,
    CompanyDeleteView,
)

app_name = "companies"

urlpatterns = [
    path("", CompanyListView.as_view(), name="list"),
    path("new/", CompanyCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", CompanyUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", CompanyDeleteView.as_view(), name="delete"),
]
