# invoices/views_invoice_pdf.py
import base64
from io import BytesIO

import qrcode
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import translation
from weasyprint import HTML

from .models import Invoice, Company


def _make_qr_data_uri(payload: str) -> str:
    img = qrcode.make(payload)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def _build_sepa_qr(company: Company, invoice: Invoice) -> str:
    """
    EPC / SEPA QR payload (European Payments Council).
    Banking apps expect this format, not plain text.
    """
    bic = (getattr(company, "company_bic", "") or "").strip()          # e.g. BELADEBEXXX
    name = (getattr(company, "company_owner", "") or "").strip()      # account holder
    iban = (getattr(company, "company_iban", "") or "").replace(" ", "").strip()

    # Amount must be like EUR123.45 (dot as decimal separator)
    amount = f"{invoice.invoice_total:.2f}".replace(",", ".")

    # Remittance info (short + safe)
    remittance = f"Invoice {invoice.invoice_no}"

    return "\n".join([
        "BCD",        # service tag
        "001",        # version
        "1",          # character set (UTF-8)
        "SCT",        # SEPA credit transfer
        bic,
        name,
        iban,
        f"EUR{amount}",
        "",           # purpose (optional)
        remittance,   # remittance information
        "",           # information (optional)
    ])


def _build_invoice_pdf_context(invoice: Invoice, company: Company, language_code: str) -> dict:
    customer = invoice.invoice_customer
    items = invoice.items.all()

    # ✅ SEPA QR (bank-scan friendly)
    qr_payload = _build_sepa_qr(company, invoice) if company else ""
    qr_data_uri = _make_qr_data_uri(qr_payload) if qr_payload else ""

    return {
        "invoice": invoice,
        "company": company,
        "customer": customer,
        "items": items,
        "qr_data_uri": qr_data_uri,
        "LANGUAGE_CODE": language_code,  # required for RTL in template
    }


@login_required
def invoice_pdf(request, pk):
    invoice = get_object_or_404(
        Invoice.objects.select_related("invoice_customer")
        .prefetch_related("items__invoice_item_diagnosis"),
        pk=pk,
    )
    company = Company.objects.first()

    language_code = translation.get_language() or "en"
    ctx = _build_invoice_pdf_context(invoice, company, language_code)

    html_string = render_to_string("invoices/invoices/invoice_pdf.html", ctx)
    pdf = HTML(string=html_string, base_url=request.build_absolute_uri("/")).write_pdf()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="invoice_{invoice.invoice_no}.pdf"'
    return response
