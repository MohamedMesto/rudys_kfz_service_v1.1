# invoices/views_invoice_pdf_reportlab.py
from io import BytesIO
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import translation
from django.utils.translation import gettext as _

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from .models import Invoice, Company

from reportlab.lib.utils import ImageReader
import qrcode
 


# def _make_qr_png_bytes(payload: str) -> bytes:
#     img = qrcode.make(payload)
#     buf = BytesIO()
#     img.save(buf, format="PNG")
#     return buf.getvalue()


# def _build_sepa_payload(company: Company, invoice: Invoice) -> str:
#     """
#     EPC / SEPA QR format (يدعمه تطبيقات البنوك الألمانية عادةً)
#     """
#     bic = (getattr(company, "company_bic", "") or "").strip()
#     iban = (company.company_iban or "").replace(" ", "")
#     name = (company.company_owner or company.company_name or "").strip()
#     amount = f"{Decimal(invoice.invoice_total):.2f}"
#     remittance = f"RE {invoice.invoice_no}"

#     # EPC069-12 standard
#     # Lines:
#     # 1: BCD
#     # 2: Version (001)
#     # 3: Character set (1 = UTF-8)
#     # 4: Identification (SCT)
#     # 5: BIC (optional but many scanners like it)
#     # 6: Name
#     # 7: IBAN
#     # 8: Amount (EUR)
#     # 9: Purpose (optional)
#     # 10: Remittance
#     # 11: Information (optional)
#     lines = [
#         "BCD",
#         "001",
#         "1",
#         "SCT",
#         bic,
#         name,
#         iban,
#         f"EUR{amount}",
#         "",
#         remittance,
#         "",
#     ]
#     return "\n".join(lines)


def _build_sepa_payload(company, invoice):
    """
    Build official EPC QR (SEPA) format.
    """
    return (
        "BCD\n"
        "001\n"
        "1\n"
        "SCT\n"
        f"{getattr(company, 'company_bic', '')}\n"
        f"{company.company_owner}\n"
        f"{company.company_iban}\n"
        "EUR{:.2f}\n"
        "\n"
        f"Invoice {invoice.invoice_no}\n"
    ).format(invoice.invoice_total)

def _money(x) -> str:
    try:
        return f"{Decimal(x):.2f} €"
    except Exception:
        return "0.00 €"


def _header_footer(c: canvas.Canvas, doc, company: Company, invoice: Invoice):
    """
    Draw header + footer on each page.
    """
    width, height = A4
    left = doc.leftMargin
    right = width - doc.rightMargin
    top = height - doc.topMargin + 12 * mm  # a bit higher than body start
    bottom = 12 * mm

    # -------------------
    # HEADER (same level)
    # -------------------
    c.saveState()

    # LEFT header block (company)
    xL = left
    y = top
    c.setFont("Helvetica-Bold", 12)
    c.drawString(xL, y, company.company_name if company else "—")
    c.setFont("Helvetica", 9)
    y -= 5 * mm
    if company and company.company_address:
        c.drawString(xL, y, str(company.company_address).replace("\n", " "))
        y -= 4 * mm
    if company and company.company_phone:
        c.drawString(xL, y, f"{_('Phone')}: {company.company_phone}")
        y -= 4 * mm
    if company and company.company_email:
        c.drawString(xL, y, f"{_('Email')}: {company.company_email}")
        y -= 4 * mm

    # RIGHT header block (invoice meta) — aligned to right, SAME TOP LINE
    xR = right
    yR = top
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(xR, yR, f"{_('Invoice')} {invoice.invoice_no}")
    c.setFont("Helvetica", 9)
    yR -= 5 * mm
    c.drawRightString(xR, yR, f"{_('Order date')}: {invoice.invoice_order_date}")
    yR -= 4 * mm
    c.drawRightString(xR, yR, f"{_('Service date')}: {invoice.invoice_service_date}")

    # header separator line
    c.setLineWidth(0.5)
    c.line(left, top - 18 * mm, right, top - 18 * mm)

    # -------------------
    # FOOTER (fixed bottom)
    # -------------------
    c.setLineWidth(0.5)
    c.line(left, bottom + 18 * mm, right, bottom + 18 * mm)

    yF = bottom + 14 * mm
    c.setFont("Helvetica", 8)

    # footer LEFT column (company info)
    xFL = left
    if company:
        c.drawString(xFL, yF, company.company_name or "")
        yF -= 4 * mm
        if company.company_address:
            # split address in 2 lines if needed
            addr_lines = str(company.company_address).splitlines() or [str(company.company_address)]
            for line in addr_lines[:2]:
                c.drawString(xFL, yF, line.strip())
                yF -= 4 * mm

        if company.company_phone:
            c.drawString(xFL, yF, f"{_('Phone')}: {company.company_phone}")
            yF -= 4 * mm
        if company.company_email:
            c.drawString(xFL, yF, f"{_('Email')}: {company.company_email}")
            yF -= 4 * mm


    # -------------------
    # QR in center footer
    # -------------------
    if company and company.company_iban and company.company_owner:
        qr_payload = _build_sepa_payload(company, invoice)

        qr_img = qrcode.make(qr_payload)
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        qr_reader = ImageReader(qr_buffer)

        qr_size = 25 * mm
        x_center = (left + right) / 2 - (qr_size / 2)
        y_qr = bottom + 4 * mm

        c.drawImage(
            qr_reader,
            x_center,
            y_qr,
            qr_size,
            qr_size,
            preserveAspectRatio=True,
            mask='auto'
        )
        
    # footer RIGHT column (bank/legal)
    xFR = right
    yFR = bottom + 14 * mm
    if company:
        if company.company_iban:
            c.drawRightString(xFR, yFR, f"IBAN: {company.company_iban}")
            yFR -= 4 * mm
        if company.company_owner:
            c.drawRightString(xFR, yFR, f"{_('Owner')}: {company.company_owner}")
            yFR -= 4 * mm
        if company.company_tax_number:
            c.drawRightString(xFR, yFR, f"{_('Tax ID')}: {company.company_tax_number}")
            yFR -= 4 * mm

    c.restoreState()


@login_required
def invoice_pdf_reportlab(request, pk):
    # Use current UI language (en/de/ar)
    lang = translation.get_language() or "en"
    translation.activate(lang)

    invoice = get_object_or_404(
        Invoice.objects.select_related("invoice_customer").prefetch_related("items"),
        pk=pk,
    )
    company = Company.objects.first()

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=35 * mm,   # enough space for header
        bottomMargin=30 * mm # enough space for footer
    )

    styles = getSampleStyleSheet()
    story = []

    # Customer block (rows under each other, left side)
    customer = invoice.invoice_customer
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(f"<b>{_('Customer')}</b>", styles["Heading3"]))
    story.append(Paragraph(f"{_('Customer number')}: {customer.customer_number}", styles["Normal"]))
    story.append(Paragraph(f"{_('Name')}: {customer.customer_name}", styles["Normal"]))
    story.append(Paragraph(f"{_('Address')}: {customer.customer_address or '—'}", styles["Normal"]))
    story.append(Paragraph(f"{_('Vehicle')}: {customer.customer_vehicle or '—'}", styles["Normal"]))
    story.append(Paragraph(f"{_('License plate number')}: {customer.customer_license_plate or '—'}", styles["Normal"]))
    story.append(Paragraph(f"{_('Mileage')}: {customer.customer_kilometers or '—'}", styles["Normal"]))
    story.append(Spacer(1, 6 * mm))

    # Intro text before table
    story.append(Paragraph(_("We thank you for your order and invoice the following items."), styles["Italic"]))
    story.append(Spacer(1, 4 * mm))

    # Items table + totals included
    data = [[
        _("Diagnosis / Service"),
        _("Quantity"),
        _("Unit price (€)"),
        _("Total"),
    ]]

    for it in invoice.items.all():
        data.append([
            it.invoice_item_diagnosis_text,
            str(it.invoice_item_quantity),
            _money(it.invoice_item_unit_price),
            _money(it.invoice_item_line_total),
        ])

    # Totals rows
    data.append(["", "", _("Subtotal"), _money(invoice.invoice_subtotal)])
    data.append(["", "", f"{_('VAT')} ({invoice.invoice_vat_percent}%)", _money(invoice.invoice_vat_amount)])
    data.append(["", "", _("Total"), _money(invoice.invoice_total)])

    tbl = Table(data, colWidths=[90*mm, 20*mm, 35*mm, 35*mm])

    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("ALIGN", (1,1), (-1,-1), "RIGHT"),
        ("ALIGN", (0,0), (0,-1), "LEFT"),
        ("FONTNAME", (0,1), (-1,-4), "Helvetica"),
        ("FONTNAME", (2,-3), (3,-1), "Helvetica-Bold"),
        ("BACKGROUND", (0,-1), (-1,-1), colors.whitesmoke),
    ]))

    story.append(tbl)

    doc.build(
        story,
        onFirstPage=lambda c, d: _header_footer(c, d, company, invoice),
        onLaterPages=lambda c, d: _header_footer(c, d, company, invoice),
    )

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="invoice_{invoice.invoice_no}_reportlab.pdf"'
    return response
