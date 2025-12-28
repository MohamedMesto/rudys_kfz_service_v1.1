# invoices/views_invoice_full.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Invoice
from .forms_invoice import InvoiceForm, InvoiceItemFormSet

@login_required
def invoice_create_view(request):
    if request.method == "POST":
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            invoice = form.save()
            formset.instance = invoice
            formset.save()
            return redirect("invoices:list")  # or another page
    else:
        form = InvoiceForm()
        formset = InvoiceItemFormSet()

    return render(request, "invoices/invoices/full_form.html", {
        "form": form,
        "formset": formset,
    })
