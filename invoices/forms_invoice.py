# invoices/forms_invoice.py
from django import forms
from django.forms import inlineformset_factory
from .models import Invoice, InvoiceItem

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "invoice_no",
            "invoice_customer",
            "invoice_order_date",
            "invoice_service_date",
            "invoice_vat_percent",
            "invoice_notes",
            "invoice_created_by",
        ]
        widgets = {
            "invoice_order_date": forms.DateInput(attrs={"type": "date"}),
            "invoice_service_date": forms.DateInput(attrs={"type": "date"}),
        }

InvoiceItemFormSet = inlineformset_factory(
    Invoice,
    InvoiceItem,
    fields=[
        "invoice_item_diagnosis",
        "invoice_item_quantity",
        "invoice_item_unit_price",
    ],
    extra=1,
    can_delete=True
)
