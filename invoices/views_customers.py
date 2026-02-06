from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Customer


class AdminOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


# --------------------
# LIST
# --------------------
class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = "invoices/customers/list.html"
    context_object_name = "customers"


# --------------------
# CREATE
# --------------------
class CustomerCreateView(LoginRequiredMixin, AdminOnlyMixin, CreateView):
    model = Customer
    template_name = "invoices/customers/form.html"
    fields = [
        "customer_number",
        "customer_name",
        "customer_address",
        "customer_vehicle",
        "customer_license_plate",
        "customer_kilometers",
    ]
    success_url = reverse_lazy("customers:list")


# --------------------
# UPDATE
# --------------------
class CustomerUpdateView(LoginRequiredMixin, AdminOnlyMixin, UpdateView):
    model = Customer
    template_name = "invoices/customers/form.html"
    fields = [
        "customer_number",
        "customer_name",
        "customer_address",
        "customer_vehicle",
        "customer_license_plate",
        "customer_kilometers",
    ]
    success_url = reverse_lazy("customers:list")


# --------------------
# DELETE
# --------------------
class CustomerDeleteView(LoginRequiredMixin, AdminOnlyMixin, DeleteView):
    model = Customer
    template_name = "invoices/customers/confirm_delete.html"
    success_url = reverse_lazy("customers:list")
