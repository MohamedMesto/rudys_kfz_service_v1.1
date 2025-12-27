# invoices/api_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from .models import Company, Customer, Diagnosis, Invoice, InvoiceItem
from .serializers import (
    CompanySerializer,
    CustomerSerializer,
    DiagnosisSerializer,
    InvoiceSerializer,
    InvoiceItemSerializer
)
from django.shortcuts import get_object_or_404

# -----------------------------
# Company ViewSet
# -----------------------------
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().order_by('-company_created_at')
    serializer_class = CompanySerializer
    permission_classes = [IsAdminUser]  # only admins can change company details

    # optional: return single company (first) via /api/company/current/
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def current(self, request):
        company = Company.objects.first()
        if not company:
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(company)
        return Response(serializer.data)

# -----------------------------
# Diagnosis ViewSet
# -----------------------------
class DiagnosisViewSet(viewsets.ModelViewSet):
    queryset = Diagnosis.objects.all().order_by('diagnosis_title')
    serializer_class = DiagnosisSerializer
    permission_classes = [IsAuthenticated]

# -----------------------------
# Customer ViewSet
# -----------------------------
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by('-customer_created_at')
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def by_number(self, request):
        number = request.query_params.get('customer_number')
        if not number:
            return Response({'detail': 'customer_number query param is required'}, status=status.HTTP_400_BAD_REQUEST)
        customer = Customer.objects.filter(customer_number=number).first()
        if not customer:
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        serializer = self.get_serializer(customer)
        return Response(serializer.data)

# -----------------------------
# Invoice ViewSet
# -----------------------------
class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all().order_by('-invoice_created_at')
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    # optional endpoint: create invoice for a new customer (client can create the customer first)
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def pdf(self, request, pk=None):
        """
        Stub for PDF generation endpoint. Implement PDF generation (WeasyPrint) separately.
        """
        invoice = get_object_or_404(Invoice, pk=pk)
        return Response({'detail': f'PDF endpoint for invoice {invoice.invoice_no} not implemented yet.'}, status=status.HTTP_501_NOT_IMPLEMENTED)

# -----------------------------
# InvoiceItem ViewSet (rarely used directly)
# -----------------------------
class InvoiceItemViewSet(viewsets.ModelViewSet):
    queryset = InvoiceItem.objects.all().order_by('invoice_item_invoice_id', 'invoice_item_pos')
    serializer_class = InvoiceItemSerializer
    permission_classes = [IsAuthenticated]
