from django.urls import path
from .views_customers import (
    CustomerListView,
    CustomerCreateView,
    CustomerUpdateView,
    CustomerDeleteView,
)

app_name = "customers"

urlpatterns = [
    path("", CustomerListView.as_view(), name="list"),
    path("new/", CustomerCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", CustomerUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", CustomerDeleteView.as_view(), name="delete"),
]
