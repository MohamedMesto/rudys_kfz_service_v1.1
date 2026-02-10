"""rudys_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
 
 
# rudys_project/urls.py

from django.contrib import admin
from django.urls import path, include
from invoices.views import home_view

urlpatterns = [
    path("admin/", admin.site.urls),

    # Homepage
    path("", home_view, name="home"),

    # i18n
    path("i18n/", include("django.conf.urls.i18n")),

    # Invoices app (main)
    path("", include("invoices.urls")),

    # API
    path("api/", include("invoices.api_urls")),

    # Feature modules
    path("companies/", include("invoices.urls_companies", namespace="companies")),
    path("customers/", include("invoices.urls_customers", namespace="customers")),
    path("diagnoses/", include("invoices.urls_diagnoses", namespace="diagnoses")),
    path("invoices/", include("invoices.urls_invoices", namespace="invoices")),


    # auth urls (new)
    path("accounts/", include("invoices.urls_auth", namespace="auth")),

]
