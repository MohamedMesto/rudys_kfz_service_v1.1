# invoices/admin.py
from django.contrib import admin
from django import forms
from .models import (
    Company,
    Profile,
    Customer,
    Diagnosis,
    Invoice,
    InvoiceItem,
)


# -----------------------------
# InvoiceItem Inline for Invoice
# -----------------------------

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0

    # SHOW ONLY WHAT USER SHOULD SEE
    fields = (
        'invoice_item_pos',
        'invoice_item_diagnosis_id',  # 👈 dropdown
        'invoice_item_quantity',
        'invoice_item_unit_price',
        'invoice_item_line_total',
    )

    readonly_fields = (
        'invoice_item_pos',           # 👈 read-only
        'invoice_item_line_total',)

    # UX improvement
    autocomplete_fields = ('invoice_item_diagnosis_id',)
    

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Rename the FK field label
        formset.form.base_fields[
            'invoice_item_diagnosis_id'
        ].label = "Diagnosis Text"
        return formset

 
 
# -----------------------------
# Company Admin
# -----------------------------
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("company_name", "company_owner", "company_email")
    readonly_fields = ("company_created_at", "company_updated_at")

    fieldsets = (
        ("Unternehmen", {
            "fields": ("company_name", "company_owner")
        }),
        ("Kontakt", {
            "fields": (
                "company_address",
                "company_phone",
                "company_email",
                "company_website",
            )
        }),
        ("Finanzen", {
            "fields": ("company_iban", "company_tax_number")
        }),
        ("System", {
            "fields": ("company_created_at", "company_updated_at")
        }),
    )


# -----------------------------
# Profile Admin
# -----------------------------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("profile_user_id", "profile_role", "profile_phone")
    search_fields = ("profile_user_id__username", "profile_role")
    readonly_fields = ("profile_created_at", "profile_updated_at")


# -----------------------------
# Customer Admin
# -----------------------------
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("customer_number", "customer_name", "customer_license_plate")
    search_fields = ("customer_number", "customer_name", "customer_license_plate")
    list_filter = ("customer_vehicle",)
    readonly_fields = ("customer_created_at", "customer_updated_at")


# -----------------------------
# Diagnosis Admin
# -----------------------------
@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ("diagnosis_title", "diagnosis_default_price")
    search_fields = ("diagnosis_title",)
    readonly_fields = ("diagnosis_created_at", "diagnosis_updated_at")


# -----------------------------
# Invoice Admin
# -----------------------------
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_no", "invoice_customer_id", "invoice_total", "invoice_order_date")
    search_fields = ("invoice_no", "invoice_customer_id__customer_name")
    list_filter = ("invoice_order_date", "invoice_service_date")
    readonly_fields = (
        "invoice_subtotal",
        "invoice_vat_amount",
        "invoice_total",
        "invoice_created_at",
        "invoice_updated_at",
    )

    inlines = [InvoiceItemInline]

    fieldsets = (
        ("Rechnungsdaten", {
            "fields": (
                "invoice_no",
                "invoice_customer_id",
                "invoice_order_date",
                "invoice_service_date",
            )
        }),
        ("Steuer & Summen", {
            "fields": (
                "invoice_subtotal",
                "invoice_vat_percent",
                "invoice_vat_amount",
                "invoice_total",
            )
        }),
        ("Sonstiges", {
            "fields": (
                "invoice_notes",
                "invoice_created_by",
                "invoice_created_at",
                "invoice_updated_at",
            )
        }),
    )



