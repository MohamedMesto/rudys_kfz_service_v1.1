# invoices/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# -----------------------
# Company Table
# -----------------------
class Company(models.Model):
    company_name = models.CharField(_("Company name"), max_length=255)
    company_address = models.TextField(_("Company address"), blank=True, null=True)
    company_phone = models.CharField(_("Company phone"), max_length=128, blank=True, null=True)
    company_email = models.EmailField(_("Company email"), blank=True, null=True)
    company_website = models.CharField(_("Company website"), max_length=255, blank=True, null=True)
    company_owner = models.CharField(_("Company owner"), max_length=255, blank=True, null=True)
    company_iban = models.CharField(_("Company IBAN"), max_length=64, blank=True, null=True)
    company_bic = models.CharField(_("BIC"), max_length=11, blank=True, null=True)
    company_tax_number = models.CharField(_("Company tax number"), max_length=64, blank=True, null=True)

    company_created_at = models.DateTimeField(auto_now_add=True)
    company_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")

    def __str__(self):
        return self.company_name


# -----------------------
# Profile Table
# -----------------------
class Profile(models.Model):
    # Selecting “account type” (Admin / Mechanic / Accountant)
    ROLE_ADMIN = "Admin"
    ROLE_MECHANIC = "Mechanic"
    ROLE_ACCOUNTANT = "Accountant"

    ROLE_CHOICES = [
        (ROLE_ADMIN, _("Admin")),
        (ROLE_MECHANIC, _("Mechanic")),
        (ROLE_ACCOUNTANT, _("Accountant")),
    ]

    profile_user_id = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("User"),
    )
    profile_role = models.CharField(
        _("Role"),
        max_length=32,
        choices=ROLE_CHOICES,
        default=ROLE_MECHANIC,   # ✅ important so it never becomes NULL/empty
    )
    profile_phone = models.CharField(_("Phone"), max_length=32, blank=True, null=True)
    profile_address = models.TextField(_("Address"), blank=True, null=True)
    profile_photo = models.ImageField(_("Photo"), upload_to="profile_photos/", blank=True, null=True)

    profile_created_at = models.DateTimeField(auto_now_add=True)
    profile_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def __str__(self):
        return f"{self.profile_user_id.username} ({self.profile_role})"



# -----------------------
# Customer Table
# -----------------------
class Customer(models.Model):
    customer_number = models.CharField(_("Customer number"), max_length=64, unique=True)
    customer_name = models.CharField(_("Customer name"), max_length=255)
    customer_address = models.TextField(_("Customer address"), blank=True, null=True)
    customer_vehicle = models.CharField(_("Vehicle"), max_length=255, blank=True, null=True)
    customer_license_plate = models.CharField(_("License plate number"), max_length=32, blank=True, null=True)
    customer_kilometers = models.PositiveIntegerField(_("Mileage"), blank=True, null=True)

    customer_created_at = models.DateTimeField(auto_now_add=True)
    customer_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")

    def __str__(self):
        return f"{self.customer_name} ({self.customer_number})"


# -----------------------
# Diagnosis Table
# -----------------------
class Diagnosis(models.Model):
    diagnosis_id = models.AutoField(primary_key=True)  # explicit primary key
    diagnosis_title = models.CharField(_("Diagnosis title"), max_length=255, unique=True)
    diagnosis_default_price = models.DecimalField(
        _("Default price (€)"),
        max_digits=10,
        decimal_places=2,
        default=0.00,
    )
    diagnosis_created_at = models.DateTimeField(auto_now_add=True)
    diagnosis_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Diagnosis")
        verbose_name_plural = _("Diagnoses")

    def __str__(self):
        return self.diagnosis_title


# -----------------------
# Invoice Table
# -----------------------
class Invoice(models.Model):
    invoice_no = models.CharField(_("Invoice number"), max_length=64, unique=True)
    invoice_customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="invoices",
        verbose_name=_("Customer"),
    )
    invoice_order_date = models.DateField(_("Order Date"), default=timezone.now)
    invoice_service_date = models.DateField(_("Service Date"), default=timezone.now)

    invoice_subtotal = models.DecimalField(_("Subtotal"), max_digits=12, decimal_places=2, default=0.00)
    invoice_vat_percent = models.DecimalField(_("VAT"), max_digits=5, decimal_places=2, default=19.00)
    invoice_vat_amount = models.DecimalField(_("VAT amount"), max_digits=12, decimal_places=2, default=0.00)
    invoice_total = models.DecimalField(_("Total"), max_digits=12, decimal_places=2, default=0.00)

    invoice_created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Created by"),
    )
    invoice_notes = models.TextField(_("Notes"), blank=True, null=True)

    invoice_created_at = models.DateTimeField(auto_now_add=True)
    invoice_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")

    def recalc_totals(self):
        items = self.items.all()
        subtotal = sum(item.invoice_item_line_total for item in items)

        self.invoice_subtotal = round(subtotal, 2)
        self.invoice_vat_amount = round(subtotal * (self.invoice_vat_percent / 100), 2)
        self.invoice_total = round(self.invoice_subtotal + self.invoice_vat_amount, 2)

        Invoice.objects.filter(pk=self.pk).update(
            invoice_subtotal=self.invoice_subtotal,
            invoice_vat_amount=self.invoice_vat_amount,
            invoice_total=self.invoice_total,
        )

    def __str__(self):
        return self.invoice_no


# -----------------------
# InvoiceItem Table
# -----------------------
class InvoiceItem(models.Model):
    invoice_item_invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("Invoice"),
    )

    invoice_item_pos = models.PositiveIntegerField(_("Position"), editable=False, null=True)

    invoice_item_diagnosis = models.ForeignKey(
        Diagnosis,
        on_delete=models.PROTECT,
        verbose_name=_("Diagnosis / Service"),
        help_text=_("Select diagnosis from predefined list"),
    )

    invoice_item_diagnosis_text = models.CharField(
        _("Diagnosis text (snapshot)"),
        max_length=255,
        editable=False,
    )

    invoice_item_quantity = models.PositiveIntegerField(_("Quantity"), default=1)
    invoice_item_unit_price = models.DecimalField(_("Unit price (€)"), max_digits=10, decimal_places=2)
    invoice_item_line_total = models.DecimalField(_("Line total (€)"), max_digits=10, decimal_places=2)

    invoice_item_created_at = models.DateTimeField(auto_now_add=True)
    invoice_item_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["invoice_item_pos"]
        verbose_name = _("Invoice item")
        verbose_name_plural = _("Invoice items")

    def save(self, *args, **kwargs):
        # Auto position per invoice
        if not self.invoice_item_pos:
            last_pos = (
                InvoiceItem.objects.filter(invoice_item_invoice=self.invoice_item_invoice)
                .aggregate(models.Max("invoice_item_pos"))
                .get("invoice_item_pos__max")
            )
            self.invoice_item_pos = (last_pos or 0) + 1

        # Snapshot diagnosis text
        self.invoice_item_diagnosis_text = self.invoice_item_diagnosis.diagnosis_title

        # Calculate line total
        self.invoice_item_line_total = self.invoice_item_quantity * self.invoice_item_unit_price

        super().save(*args, **kwargs)

        # Recalculate invoice totals AFTER saving item
        self.invoice_item_invoice.recalc_totals()

