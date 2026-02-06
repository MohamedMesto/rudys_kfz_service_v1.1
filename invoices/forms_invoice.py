# invoices/forms_invoice.py
from django import forms
from django.forms import inlineformset_factory
from .models import Invoice, InvoiceItem, Diagnosis



class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = [
            "invoice_item_diagnosis",
            "invoice_item_quantity",
            "invoice_item_unit_price",
        ]
        widgets = {
            "invoice_item_diagnosis": forms.Select(attrs={'class': 'form-select diagnosis-select'}),
            "invoice_item_quantity": forms.NumberInput(attrs={'class': 'form-control'}),
            "invoice_item_unit_price": forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    # -------------------------
    # Make invoice_no a dropdown
    # -------------------------
class InvoiceForm(forms.ModelForm):
    invoice_no = forms.ModelChoiceField(
        queryset=Invoice.objects.all(),
        empty_label="Rechnung auswählen",
        required=False,
        widget=forms.Select(attrs={
            "id": "invoice-select",
            "class": "form-select"
        })
    )

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
            "invoice_order_date": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control"
            }),
            "invoice_service_date": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control"
            }),
        }

# -------------------------
# Inline Formset for items
# -------------------------
InvoiceItemFormSet = inlineformset_factory(
    Invoice,
    InvoiceItem,
    form=InvoiceItemForm,   # ✅ THIS IS THE KEY
    fields=[
        "invoice_item_diagnosis",
        "invoice_item_quantity",
        "invoice_item_unit_price",
    ],
    extra=1,
    can_delete=True
)


