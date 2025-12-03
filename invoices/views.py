from django.shortcuts import render

def home(request):
    return render(request, 'invoices/home.html')
