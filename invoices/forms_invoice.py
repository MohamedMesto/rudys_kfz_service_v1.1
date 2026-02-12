# invoices/forms_invoice.py
from django import forms
from django.forms import inlineformset_factory
from .models import Invoice, InvoiceItem


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = [
            "invoice_item_diagnosis",
            "invoice_item_custom_text",   # ✅ NEW
            "invoice_item_quantity",
            "invoice_item_unit_price",
        ]
        widgets = {
            "invoice_item_diagnosis": forms.Select(attrs={'class': 'form-select diagnosis-select'}),
            "invoice_item_custom_text": forms.TextInput(attrs={
                "class": "form-control mt-2",
                "placeholder": "…oder neuen Text schreiben"
            }),
            "invoice_item_quantity": forms.NumberInput(attrs={'class': 'form-control'}),
            "invoice_item_unit_price": forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✅ IMPORTANT: allow empty dropdown (because user might type custom text)
        self.fields["invoice_item_diagnosis"].required = False

    def clean(self):
        cleaned = super().clean()

        diag = cleaned.get("invoice_item_diagnosis")
        txt = (cleaned.get("invoice_item_custom_text") or "").strip()

        # ✅ require at least one
        if not diag and not txt:
            raise forms.ValidationError(
                "Please select a diagnosis OR type a new one."
            )

        return cleaned


InvoiceItemFormSet = inlineformset_factory(
    Invoice,
    InvoiceItem,
    form=InvoiceItemForm,
    fields=[
        "invoice_item_diagnosis",
        "invoice_item_custom_text",   # ✅ NEW
        "invoice_item_quantity",
        "invoice_item_unit_price",
    ],
    extra=1,
    can_delete=True
)


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


# # invoices/forms_invoice.py
# from django import forms
# from django.forms import inlineformset_factory
# from .models import Invoice, InvoiceItem, Diagnosis


# # ---------------------------------------------------------
# # Invoice Item Form (one line in the invoice)
# # ---------------------------------------------------------
# class InvoiceItemForm(forms.ModelForm):
#     class Meta:
#         model = InvoiceItem
#         fields = [
#             "invoice_item_diagnosis",
#             "invoice_item_custom_text",   # ✅ NEW
#             "invoice_item_quantity",
#             "invoice_item_unit_price",
#         ]
#         widgets = {
#             "invoice_item_diagnosis": forms.Select(attrs={'class': 'form-select diagnosis-select'}),
#             "invoice_item_custom_text": forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Oder neuen Text eingeben…'
#             }),
#             "invoice_item_quantity": forms.NumberInput(attrs={'class': 'form-control'}),
#             "invoice_item_unit_price": forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
#         }


# # ---------------------------------------------------------
# # Inline Formset for invoice items
# # ---------------------------------------------------------
# InvoiceItemFormSet = inlineformset_factory(
#     parent_model=Invoice,
#     model=InvoiceItem,
#     form=InvoiceItemForm,
#     fk_name="invoice_item_invoice",   # ✅ CRITICAL for your model
#     extra=1,
#     can_delete=True,
# )
