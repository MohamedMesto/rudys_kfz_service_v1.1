# invoices/views_invoice_full.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Invoice, Company
from .forms_invoice import InvoiceForm, InvoiceItemFormSet
from django.contrib import messages
from django.http import JsonResponse


@login_required
def invoice_create_view(request):
    
    company = Company.objects.first()  # ← STEP 1: company source
    if not company:
        messages.warning(
            request,
            "Bitte legen Sie zuerst eine Firma an, bevor Sie eine Rechnung erstellen."
        )
        return redirect("companies:create")
 
    if request.method == "POST":
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            invoice = form.save()
            formset.instance = invoice
            formset.save()
            return redirect("invoices:list")
    else:
        form = InvoiceForm()
        formset = InvoiceItemFormSet()

    
    return render(request, "invoices/invoices/full_form.html", {
        "form": form,
        "formset": formset,
        "company": company,  # ← pass to template
    })

    
@login_required
def get_invoice_data(request, pk):
    invoice = Invoice.objects.get(pk=pk)
    return JsonResponse({
        'invoice_order_date': invoice.invoice_order_date.strftime('%Y-%m-%d'),
        'invoice_service_date': invoice.invoice_service_date.strftime('%Y-%m-%d'),
    })

@login_required
def get_invoice_data(request, pk):
    invoice = Invoice.objects.select_related("invoice_customer").get(pk=pk)
    customer = invoice.invoice_customer

    return JsonResponse({
        # invoice meta
        "invoice_order_date": invoice.invoice_order_date.strftime("%Y-%m-%d"),
        "invoice_service_date": invoice.invoice_service_date.strftime("%Y-%m-%d"),

        # customer data
        "customer_number": customer.customer_number,
        "customer_name": customer.customer_name,
        "customer_address": customer.customer_address or "",
        "customer_vehicle": customer.customer_vehicle or "",
        "customer_license_plate": customer.customer_license_plate or "",
        "customer_kilometers": customer.customer_kilometers or "",
        "customer_created_at": customer.customer_created_at.strftime("%Y-%m-%d"),
        "customer_updated_at": customer.customer_updated_at.strftime("%Y-%m-%d"),
    })
