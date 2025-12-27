from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import Invoice


class AdminOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


# --------------------
# LIST
# --------------------
class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = "invoices/invoices/list.html"
    context_object_name = "invoices"


# --------------------
# CREATE
# --------------------
class InvoiceCreateView(LoginRequiredMixin, AdminOnlyMixin, CreateView):
    model = Invoice
    template_name = "invoices/invoices/form.html"
    fields = [
        "invoice_number",
        "invoice_customer",
        "invoice_date",
    ]
    success_url = reverse_lazy("invoices:list")


# --------------------
# UPDATE
# --------------------
class InvoiceUpdateView(LoginRequiredMixin, AdminOnlyMixin, UpdateView):
    model = Invoice
    template_name = "invoices/invoices/form.html"
    fields = [
        "invoice_number",
        "invoice_customer",
        "invoice_date",
    ]
    success_url = reverse_lazy("invoices:list")


# --------------------
# DELETE
# --------------------
class InvoiceDeleteView(LoginRequiredMixin, AdminOnlyMixin, DeleteView):
    model = Invoice
    template_name = "invoices/invoices/confirm_delete.html"
    success_url = reverse_lazy("invoices:list")
