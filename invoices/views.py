# rudys_kfz_service_v1.1/invoices/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def home_view(request):
    return render(request, "invoices/home.html")

 
 