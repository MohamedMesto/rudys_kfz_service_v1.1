from django.urls import path
from .views_invoices import (
    InvoiceListView,
    InvoiceCreateView,
    InvoiceUpdateView,
    InvoiceDeleteView,
)
from .views import invoice_create_view

app_name = "invoices"

urlpatterns = [
    path("", InvoiceListView.as_view(), name="list"),
    path("create/", InvoiceCreateView.as_view(), name="create"),
    path("<int:pk>/update/", InvoiceUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", InvoiceDeleteView.as_view(), name="delete"),
    # invoices/urls_invoices.py
    path("full-create/", invoice_create_view, name="full_create"),

]
