# invoices/views_invoice_full.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Invoice, Company, Customer
from .forms_invoice import InvoiceForm, InvoiceItemFormSet

@login_required
def invoice_create_view(request):
    company = Company.objects.first()
    if not company:
        messages.warning(
            request,
            "Bitte legen Sie zuerst eine Firma an, bevor Sie eine Rechnung erstellen."
        )
        return redirect("companies:create")

    invoices = Invoice.objects.order_by("-id")[:200]
    customers = Customer.objects.order_by("customer_number")

    if request.method == "POST":
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)

        # 1) invoice no from "create mode" input if provided
        invoice_no_new = (request.POST.get("invoice_no_new") or "").strip()
        if invoice_no_new:
            form.data = form.data.copy()
            form.data["invoice_no"] = invoice_no_new

        # 2) customer selected from dropdown (hidden input)
        customer_id = request.POST.get("customer_id")
        if customer_id:
            form.instance.invoice_customer_id = customer_id

        if form.is_valid() and formset.is_valid():
            invoice = form.save()
            formset.instance = invoice
            formset.save()
            return redirect("invoices:list")

    else:
        form = InvoiceForm()
        formset = InvoiceItemFormSet()

    return render(
        request,
        "invoices/invoices/full_form.html",
        {
            "form": form,
            "formset": formset,
            "company": company,
            "invoices": invoices,
            "customers": customers,
        },
    )

@login_required
def get_customer_data(request, pk):
    customer = Customer.objects.get(pk=pk)
    return JsonResponse({
        "customer_number": customer.customer_number,
        "customer_name": customer.customer_name,
        "customer_address": customer.customer_address or "",
        "customer_vehicle": customer.customer_vehicle or "",
        "customer_license_plate": customer.customer_license_plate or "",
        "customer_kilometers": customer.customer_kilometers or "",
        "customer_created_at": customer.customer_created_at.strftime("%Y-%m-%d"),
        "customer_updated_at": customer.customer_updated_at.strftime("%Y-%m-%d"),
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

        # totals
        "subtotal": float(invoice.invoice_subtotal),
        "vat_percent": float(invoice.invoice_vat_percent),
        "vat_amount": float(invoice.invoice_vat_amount),
        "grand_total": float(invoice.invoice_total),
    })


@login_required
def get_invoice_items(request, pk):
    invoice = Invoice.objects.prefetch_related(
        "items__invoice_item_diagnosis"
    ).get(pk=pk)

    # ⚡ Ensure DB totals are fresh
    invoice.recalc_totals()
    items_data = []
   

    for item in invoice.items.all():
        # line_total = float(item.invoice_item_quantity * item.invoice_item_unit_price)
       

        items_data.append({
            "diagnosis_id": item.invoice_item_diagnosis_id,     # ✅ KEEP
            "diagnosis_text": item.invoice_item_diagnosis_text, # ✅ KEEP
            "quantity": item.invoice_item_quantity,
            "unit_price": float(item.invoice_item_unit_price),
            "line_total": float(item.invoice_item_line_total),
        })

 

    return JsonResponse({
        "items": items_data,
        # ✅ USE DB FIELDS – NO CALCULATION


        "subtotal": float(invoice.invoice_subtotal or 0),
        "vat_percent": float(invoice.invoice_vat_percent or 0),
        "vat_amount": float(invoice.invoice_vat_amount or 0),
        "grand_total": float(invoice.invoice_total or 0),

    })

 
