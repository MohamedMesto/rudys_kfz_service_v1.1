# invoices/urls.py
from django.urls import path,include
from . import views

app_name = 'invoices'

urlpatterns = [
    path('invoices/new/', views.invoice_create_view, name='invoice-create'),
    path('invoices/', views.invoice_list_view, name='invoice-list'),
    path('invoices/<int:invoice_id>/', views.invoice_detail_view, name='invoice-detail'),
    path("companies/", include("invoices.urls_companies")),
    path("customers/", include("invoices.urls_customers")),
    path("diagnoses/", include("invoices.urls_diagnoses", namespace="diagnoses")),
]
