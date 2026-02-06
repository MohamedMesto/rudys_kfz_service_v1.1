# rudys_kfz_service_v1.1/invoices/urls_invoices.py

from django.urls import path
from .views_invoices import (
    InvoiceListView,
    InvoiceCreateView,
    InvoiceUpdateView,
    InvoiceDeleteView,
)
from .views_invoice_full import invoice_create_view,get_invoice_data,get_invoice_items
 

app_name = "invoices"

urlpatterns = [
    path("", InvoiceListView.as_view(), name="list"),
    path("create/", InvoiceCreateView.as_view(), name="create"),
    path("<int:pk>/update/", InvoiceUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", InvoiceDeleteView.as_view(), name="delete"),
    # Full invoice UI
    path("full-create/", invoice_create_view, name="full_create"),


    # AJAX
    path("get-invoice-data/<int:pk>/", get_invoice_data, name="get_invoice_data"),
    path("get-invoice-items/<int:pk>/", get_invoice_items, name="get_invoice_items"),


]
