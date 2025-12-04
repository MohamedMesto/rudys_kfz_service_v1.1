# invoices/api_urls.py
from rest_framework import routers
from .api_views import (
    CompanyViewSet,
    DiagnoseViewSet,
    CustomerViewSet,
    InvoiceViewSet,
    InvoiceItemViewSet
)
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'company', CompanyViewSet, basename='company')
router.register(r'diagnose', DiagnoseViewSet, basename='diagnose')
router.register(r'customers', CustomerViewSet, basename='customers')
router.register(r'invoices', InvoiceViewSet, basename='invoices')
router.register(r'invoice-items', InvoiceItemViewSet, basename='invoice-items')

urlpatterns = [
    path('', include(router.urls)),
]
