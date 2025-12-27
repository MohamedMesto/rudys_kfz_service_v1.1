from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import Diagnosis


class AdminOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


# --------------------
# LIST
# --------------------
class DiagnosisListView(LoginRequiredMixin, ListView):
    model = Diagnosis
    template_name = "invoices/diagnoses/list.html"
    context_object_name = "diagnoses"
    ordering = ["diagnosis_title"]


# --------------------
# CREATE
# --------------------
class DiagnosisCreateView(LoginRequiredMixin, AdminOnlyMixin, CreateView):
    model = Diagnosis
    template_name = "invoices/diagnoses/form.html"
    fields = ["diagnosis_title", "diagnosis_default_price"]
    success_url = reverse_lazy("diagnoses:list")


# --------------------
# UPDATE
# --------------------
class DiagnosisUpdateView(LoginRequiredMixin, AdminOnlyMixin, UpdateView):
    model = Diagnosis
    template_name = "invoices/diagnoses/form.html"
    fields = ["diagnosis_title", "diagnosis_default_price"]
    success_url = reverse_lazy("diagnoses:list")


# --------------------
# DELETE
# --------------------
class DiagnosisDeleteView(LoginRequiredMixin, AdminOnlyMixin, DeleteView):
    model = Diagnosis
    template_name = "invoices/diagnoses/confirm_delete.html"
    success_url = reverse_lazy("diagnoses:list")
