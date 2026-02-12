# invoices/urls_invoices.py
from django.urls import path
from .views_invoices import (
    InvoiceListView,
    InvoiceCreateView,
    InvoiceUpdateView,
    InvoiceDeleteView,
    check_invoice_no,
)
from .views_invoice_full import (
    invoice_create_view,
    get_invoice_data,
    get_invoice_items,
    get_customer_data,
    
)

from .views_invoice_pdf_reportlab import invoice_pdf_reportlab
from .views_invoice_pdf import invoice_pdf  # (WeasyPrint - only on Ubuntu HTML2PDF)


app_name = "invoices"

urlpatterns = [
    path("", InvoiceListView.as_view(), name="list"),
    path("create/", InvoiceCreateView.as_view(), name="create"),
    path("<int:pk>/update/", InvoiceUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", InvoiceDeleteView.as_view(), name="delete"),

    # Full invoice UI
    path("full-create/", invoice_create_view, name="full_create"),

 
    # AJAX (keep underscore style to match your existing working links)
    path("get_invoice_data/<int:pk>/", get_invoice_data, name="get_invoice_data"),
    path("get_invoice_items/<int:pk>/", get_invoice_items, name="get_invoice_items"),
    path("get_customer_data/<int:pk>/", get_customer_data, name="get_customer_data"),
    path("check_invoice_no/", check_invoice_no, name="check_invoice_no"),
    # PDF
    path("<int:pk>/pdf/", invoice_pdf, name="pdf"),  # (WeasyPrint - only on Ubuntu HTML2PDF)
    path("<int:pk>/pdf-rl/", invoice_pdf_reportlab, name="pdf_rl"),  #  (ReportLab on Ubuntu ans Windows - HTML2PDF)

    ]
 