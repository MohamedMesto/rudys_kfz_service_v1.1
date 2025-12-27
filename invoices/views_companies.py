from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Company


class AdminOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


# --------------------
# LIST
# --------------------
class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    template_name = "invoices/companies/list.html"
    context_object_name = "companies"


# --------------------
# CREATE
# --------------------
class CompanyCreateView(LoginRequiredMixin, AdminOnlyMixin, CreateView):
    model = Company
    template_name = "invoices/companies/form.html"
    fields = [
        "company_name",
        "company_address",
        "company_phone",
        "company_email",
        "company_website",
        "company_owner",
        "company_iban",
        "company_tax_number",
    ]
    success_url = reverse_lazy("companies:list")


# --------------------
# UPDATE
# --------------------
class CompanyUpdateView(LoginRequiredMixin, AdminOnlyMixin, UpdateView):
    model = Company
    template_name = "invoices/companies/form.html"
    fields = [
        "company_name",
        "company_address",
        "company_phone",
        "company_email",
        "company_website",
        "company_owner",
        "company_iban",
        "company_tax_number",
    ]
    success_url = reverse_lazy("companies:list")


# --------------------
# DELETE
# --------------------
class CompanyDeleteView(LoginRequiredMixin, AdminOnlyMixin, DeleteView):
    model = Company
    template_name = "invoices/companies/confirm_delete.html"
    success_url = reverse_lazy("companies:list")
