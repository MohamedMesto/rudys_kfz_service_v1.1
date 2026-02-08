# # invoices/forms_invoice.py
# from django import forms
# from django.forms import inlineformset_factory
# from .models import Invoice, InvoiceItem, Diagnosis
 

# invoices/forms_invoice.py
from django import forms
from django.forms import inlineformset_factory
from .models import Invoice, InvoiceItem


# ---------------------------------------------------------
# Invoice Item Form (one line in the invoice)
# ---------------------------------------------------------
class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = [
            "invoice_item_diagnosis",
            "invoice_item_quantity",
            "invoice_item_unit_price",
        ]
        widgets = {
            "invoice_item_diagnosis": forms.Select(
                attrs={"class": "form-select diagnosis-select"}
            ),
            "invoice_item_quantity": forms.NumberInput(
                attrs={"class": "form-control", "min": "1"}
            ),
            "invoice_item_unit_price": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
        }


# ---------------------------------------------------------
# Invoice Form (header/meta)
# ---------------------------------------------------------
class InvoiceForm(forms.ModelForm):
    # ✅ This is ONLY for selecting an existing invoice (UI helper)
    # It does NOT map to the model. We use it for JS selection only.
    invoice_select = forms.ModelChoiceField(
        queryset=Invoice.objects.select_related("invoice_customer").order_by("-id"),
        required=False,
        empty_label="Rechnung auswählen",
        widget=forms.Select(attrs={"id": "invoice-select", "class": "form-select"}),
        label="",
    )

    class Meta:
        model = Invoice
        fields = [
            "invoice_no",           # ✅ real CharField (typed for new invoice)
            "invoice_customer",     # ✅ FK saved correctly
            "invoice_order_date",
            "invoice_service_date",
            "invoice_vat_percent",
            "invoice_notes",
        ]
        widgets = {
            "invoice_no": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "off",
                }
            ),
            "invoice_customer": forms.Select(
                attrs={"class": "form-select", "id": "customer-select"}
            ),
            "invoice_order_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "invoice_service_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "invoice_vat_percent": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "invoice_notes": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
        }

    def clean_invoice_no(self):
        """
        Keep invoice_no as text, but strip spaces to avoid duplicates like 'INV1 '.
        """
        value = (self.cleaned_data.get("invoice_no") or "").strip()
        return value


# ---------------------------------------------------------
# Inline Formset for invoice items
# ---------------------------------------------------------
InvoiceItemFormSet = inlineformset_factory(
    parent_model=Invoice,
    model=InvoiceItem,
    form=InvoiceItemForm,
    fk_name="invoice_item_invoice",   # ✅ CRITICAL for your model
    extra=1,
    can_delete=True,
)


# class InvoiceItemForm(forms.ModelForm):
#     class Meta:
#         model = InvoiceItem
#         fields = [
#             "invoice_item_diagnosis",
#             "invoice_item_quantity",
#             "invoice_item_unit_price",
#         ]
#         widgets = {
#             "invoice_item_diagnosis": forms.Select(attrs={'class': 'form-select diagnosis-select'}),
#             "invoice_item_quantity": forms.NumberInput(attrs={'class': 'form-control'}),
#             "invoice_item_unit_price": forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
#         }

#     # -------------------------
#     # Make invoice_no a dropdown
#     # -------------------------
# class InvoiceForm(forms.ModelForm):
#     invoice_no = forms.ModelChoiceField(
#         queryset=Invoice.objects.all(),
#         empty_label="Rechnung auswählen",
#         required=False,
#         widget=forms.Select(attrs={
#             "id": "invoice-select",
#             "class": "form-select"
#         })
#     )

#     class Meta:
#         model = Invoice
#         fields = [
#             "invoice_no",
#             "invoice_customer",
#             "invoice_order_date",
#             "invoice_service_date",
#             "invoice_vat_percent",
#             "invoice_notes",
#             "invoice_created_by",
#         ]
#         widgets = {
#             "invoice_order_date": forms.DateInput(attrs={
#                 "type": "date",
#                 "class": "form-control"
#             }),
#             "invoice_service_date": forms.DateInput(attrs={
#                 "type": "date",
#                 "class": "form-control"
#             }),
#         }

# # -------------------------
# # Inline Formset for items
# # -------------------------
# InvoiceItemFormSet = inlineformset_factory(
#     Invoice,
#     InvoiceItem,
#     form=InvoiceItemForm,   # ✅ THIS IS THE KEY
#     fields=[
#         "invoice_item_diagnosis",
#         "invoice_item_quantity",
#         "invoice_item_unit_price",
#     ],
#     extra=1,
#     can_delete=True
# )


