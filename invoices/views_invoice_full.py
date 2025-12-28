# invoices/views_invoice_full.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Invoice, Company
from .forms_invoice import InvoiceForm, InvoiceItemFormSet
from django.contrib import messages
 
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

    