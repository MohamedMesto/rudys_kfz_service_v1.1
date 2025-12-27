# invoices/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Company, Diagnosis, Invoice, Customer

@login_required
def home_view(request):
    return render(request, 'invoices/home.html')

@login_required
def invoice_create_view(request):
    # We will let the frontend call the API to create (DRF).
    company = Company.objects.first()
    diagnosiss = Diagnosis.objects.all()
    context = {
        'company': company,
        'diagnosiss': diagnosiss,
    }
    return render(request, 'invoices/invoice_form.html', context)

@login_required
def invoice_list_view(request):
    return render(request, 'invoices/invoice_list.html', {})

@login_required
def invoice_detail_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    return render(request, 'invoices/invoice_detail.html', {'invoice': invoice})
