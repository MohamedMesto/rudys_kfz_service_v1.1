# invoices/serializers.py
from decimal import Decimal, ROUND_HALF_UP
from rest_framework import serializers
from django.db import transaction
from .models import (
    Company,
    Customer,
    Diagnosis,
    Invoice,
    InvoiceItem,
)
from django.contrib.auth import get_user_model

User = get_user_model()

# Helper for rounding currency values
def quantize_currency(value):
    if value is None:
        return Decimal('0.00')
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

# -----------------------------
# Company Serializer
# -----------------------------
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id',
            'company_name',
            'company_address',
            'company_phone',
            'company_email',
            'company_website',
            'company_owner',
            'company_iban',
            'company_tax_number',
            'company_created_at',
            'company_updated_at',
        ]
        read_only_fields = ('company_created_at', 'company_updated_at')

# # -----------------------------
# # Diagnosis Serializer
# # -----------------------------
# class DiagnosisSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Diagnosis
#         fields = [
#             'id',
#             'diagnosis_title',
#             'diagnosis_default_price',
#             'diagnosis_created_at',
#             'diagnosis_updated_at',
#         ]
#         read_only_fields = ('diagnosis_created_at', 'diagnosis_updated_at')

# -----------------------------
# Customer Serializer
# -----------------------------
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'id',
            'customer_number',
            'customer_name',
            'customer_address',
            'customer_vehicle',
            'customer_license_plate',
            'customer_kilometers',
            'customer_created_at',
            'customer_updated_at',
        ]
        read_only_fields = ('customer_created_at', 'customer_updated_at')

# -----------------------------
# InvoiceItem Serializer (nested)
# -----------------------------

# class InvoiceItemSerializer(serializers.ModelSerializer):
#     # FK by ID
#     invoice_item_diagnosis_id = serializers.PrimaryKeyRelatedField(
#         queryset=Diagnosis.objects.all(),
#         allow_null=True,
#         required=False
#     )
#     # read-only convenience field
#     diagnosis_title = serializers.CharField(
#         source='invoice_item_diagnosis_id.diagnosis_title',
#         read_only=True
#     )

#     class Meta:
#         model = InvoiceItem
#         fields = [
#             'id',
#             'invoice_item_pos',
#             'invoice_item_diagnosis_id',   # numeric FK, editable
#             'diagnosis_title',             # read-only
#             'invoice_item_diagnosis_text', # editable text
#             'invoice_item_quantity',
#             'invoice_item_unit_price',
#             'invoice_item_line_total',
#         ]
#         read_only_fields = ('invoice_item_line_total', 'diagnosis_title')

#     def create(self, validated_data):
#         diag = validated_data.get('invoice_item_diagnosis_id', None)
#         # If diagnosis_text is empty, fill with title
#         if diag and not validated_data.get('invoice_item_diagnosis_text'):
#             validated_data['invoice_item_diagnosis_text'] = diag.diagnosis_title
#         qty = validated_data.get('invoice_item_quantity', 1)
#         price = quantize_currency(validated_data.get('invoice_item_unit_price', 0))
#         validated_data['invoice_item_line_total'] = quantize_currency(qty * price)
#         return super().create(validated_data)

#     def update(self, instance, validated_data):
#         diag = validated_data.get('invoice_item_diagnosis_id', instance.invoice_item_diagnosis_id)
#         instance.invoice_item_diagnosis_id = diag
#         # Only fill text if empty
#         if diag and not validated_data.get('invoice_item_diagnosis_text') and not instance.invoice_item_diagnosis_text:
#             instance.invoice_item_diagnosis_text = diag.diagnosis_title
#         # allow user to override text
#         instance.invoice_item_diagnosis_text = validated_data.get('invoice_item_diagnosis_text', instance.invoice_item_diagnosis_text)
#         instance.invoice_item_quantity = validated_data.get('invoice_item_quantity', instance.invoice_item_quantity)
#         instance.invoice_item_unit_price = quantize_currency(validated_data.get('invoice_item_unit_price', instance.invoice_item_unit_price))
#         instance.invoice_item_line_total = quantize_currency(instance.invoice_item_quantity * instance.invoice_item_unit_price)
#         instance.save()
#         return instance


# class InvoiceItemSerializer(serializers.ModelSerializer):
#     invoice_item_diagnosis_id = serializers.PrimaryKeyRelatedField(
#         queryset=Diagnosis.objects.all(),
#         allow_null=True,
#         required=False
#     )
#     diagnosis_title = serializers.CharField(
#         source='invoice_item_diagnosis_id.diagnosis_title',
#         read_only=True
#     )

#     class Meta:
#         model = InvoiceItem
#         fields = [
#             'id',
#             'invoice_item_pos',
#             'invoice_item_diagnosis_id',   # numeric FK
#             'diagnosis_title',             # read-only convenience
#             'invoice_item_diagnosis_text', # pre-filled from FK
#             'invoice_item_quantity',
#             'invoice_item_unit_price',
#             'invoice_item_line_total',
#         ]
#         read_only_fields = ('invoice_item_line_total', 'diagnosis_title')

#     def create(self, validated_data):
#         diag = validated_data.get('invoice_item_diagnosis_id')
#         if diag and not validated_data.get('invoice_item_diagnosis_text'):
#             validated_data['invoice_item_diagnosis_text'] = diag.diagnosis_title
#         return super().create(validated_data)

#     def update(self, instance, validated_data):
#         diag = validated_data.get('invoice_item_diagnosis_id', instance.invoice_item_diagnosis_id)
#         instance.invoice_item_diagnosis_id = diag
#         # auto-fill text if blank
#         if diag and not validated_data.get('invoice_item_diagnosis_text') and not instance.invoice_item_diagnosis_text:
#             instance.invoice_item_diagnosis_text = diag.diagnosis_title
#         instance.invoice_item_diagnosis_text = validated_data.get('invoice_item_diagnosis_text', instance.invoice_item_diagnosis_text)
#         instance.invoice_item_quantity = validated_data.get('invoice_item_quantity', instance.invoice_item_quantity)
#         instance.invoice_item_unit_price = validated_data.get('invoice_item_unit_price', instance.invoice_item_unit_price)
#         instance.invoice_item_line_total = round(float(instance.invoice_item_quantity) * float(instance.invoice_item_unit_price), 2)
#         instance.save()
#         return instance


# -----------------------------
# Diagnosis Serializer
# -----------------------------
class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnosis
        fields = [
            'id',
            'diagnosis_title',
            'diagnosis_default_price',
            'diagnosis_created_at',
            'diagnosis_updated_at',
        ]
        read_only_fields = ('diagnosis_created_at', 'diagnosis_updated_at')


# -----------------------------
# InvoiceItem Serializer
# -----------------------------
class InvoiceItemSerializer(serializers.ModelSerializer):
    # Dynamic dropdown for API
    invoice_item_diagnosis_text = serializers.ChoiceField(
        choices=[(d.diagnosis_title, d.diagnosis_title) for d in Diagnosis.objects.all()]
    )

    class Meta:
        model = InvoiceItem
        fields = [
            'invoice_item_pos',
            'invoice_item_diagnosis_text',
            'invoice_item_quantity',
            'invoice_item_unit_price',
        ]

    def create(self, validated_data):
        diagnosis_text = validated_data.get('invoice_item_diagnosis_text')
        try:
            diag = Diagnosis.objects.get(diagnosis_title=diagnosis_text)
            validated_data['invoice_item_diagnosis_id'] = diag
            validated_data['invoice_item_unit_price'] = diag.diagnosis_default_price
        except Diagnosis.DoesNotExist:
            validated_data['invoice_item_diagnosis_id'] = None

        return super().create(validated_data)

    def update(self, instance, validated_data):
        diagnosis_text = validated_data.get(
            'invoice_item_diagnosis_text',
            instance.invoice_item_diagnosis_text
        )
        try:
            diag = Diagnosis.objects.get(diagnosis_title=diagnosis_text)
            instance.invoice_item_diagnosis_id = diag
            instance.invoice_item_unit_price = diag.diagnosis_default_price
        except Diagnosis.DoesNotExist:
            instance.invoice_item_diagnosis_id = None

        instance.invoice_item_diagnosis_text = diagnosis_text
        instance.invoice_item_quantity = validated_data.get(
            'invoice_item_quantity', instance.invoice_item_quantity
        )
        instance.invoice_item_unit_price = validated_data.get(
            'invoice_item_unit_price', instance.invoice_item_unit_price
        )
        instance.invoice_item_line_total = round(
            float(instance.invoice_item_quantity) * float(instance.invoice_item_unit_price), 2
        )
        instance.save()
        return instance

# -----------------------------
# Invoice Serializer (nested items)
# -----------------------------
class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, write_only=True)
    items_read = InvoiceItemSerializer(many=True, read_only=True, source='items')
    invoice_customer_id = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())

    class Meta:
        model = Invoice
        fields = [
            'id',
            'invoice_no',
            'invoice_customer_id',
            'invoice_order_date',
            'invoice_service_date',
            'invoice_subtotal',
            'invoice_vat_percent',
            'invoice_vat_amount',
            'invoice_total',
            'invoice_created_by',
            'invoice_notes',
            'items',
            'items_read',
            'invoice_created_at',
            'invoice_updated_at',
        ]
        read_only_fields = (
            'invoice_subtotal',
            'invoice_vat_amount',
            'invoice_total',
            'invoice_created_at',
            'invoice_updated_at',
        )

    def validate_invoice_no(self, value):
        # ensure invoice_no is unique (on create)
        if self.instance is None and Invoice.objects.filter(invoice_no=value).exists():
            raise serializers.ValidationError("invoice_no already exists.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        # set created_by from context (request.user) if present
        request = self.context.get('request', None)
        if request and request.user and request.user.is_authenticated:
            validated_data['invoice_created_by'] = request.user

        invoice = Invoice.objects.create(**validated_data)

        # create items; ensure pos order consistent
        for i, item in enumerate(items_data, start=1):
            item['invoice_item_invoice_id'] = invoice
            # set pos if not provided
            if 'invoice_item_pos' not in item or not item['invoice_item_pos']:
                item['invoice_item_pos'] = i
            # compute line total via serializer create logic
            serializer = InvoiceItemSerializer(data=item)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        # recalc invoice totals in a Decimal-safe way
        items_qs = invoice.items.all()
        subtotal = sum([quantize_currency(i.invoice_item_line_total) for i in items_qs])
        invoice.invoice_subtotal = quantize_currency(subtotal)
        invoice.invoice_vat_amount = quantize_currency(subtotal * quantize_currency(invoice.invoice_vat_percent) / Decimal('100'))
        invoice.invoice_total = quantize_currency(invoice.invoice_subtotal + invoice.invoice_vat_amount)
        invoice.save()
        return invoice

    @transaction.atomic
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        # update simple fields
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()

        if items_data is not None:
            # delete existing items and recreate
            instance.items.all().delete()
            for i, item in enumerate(items_data, start=1):
                item['invoice_item_invoice_id'] = instance
                if 'invoice_item_pos' not in item or not item['invoice_item_pos']:
                    item['invoice_item_pos'] = i
                serializer = InvoiceItemSerializer(data=item)
                serializer.is_valid(raise_exception=True)
                serializer.save()

        # recompute totals
        items_qs = instance.items.all()
        subtotal = sum([quantize_currency(i.invoice_item_line_total) for i in items_qs])
        instance.invoice_subtotal = quantize_currency(subtotal)
        instance.invoice_vat_amount = quantize_currency(subtotal * quantize_currency(instance.invoice_vat_percent) / Decimal('100'))
        instance.invoice_total = quantize_currency(instance.invoice_subtotal + instance.invoice_vat_amount)
        instance.save()
        return instance
