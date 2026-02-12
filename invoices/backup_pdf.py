# invoices/views_invoice_pdf_reportlab.py
from io import BytesIO
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors

import qrcode

from .models import Invoice, Company


def _make_qr_png_bytes(payload: str) -> bytes:
    img = qrcode.make(payload)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _build_sepa_payload(company: Company, invoice: Invoice) -> str:
    """
    EPC / SEPA QR format (يدعمه تطبيقات البنوك الألمانية عادةً)
    """
    bic = (getattr(company, "company_bic", "") or "").strip()
    iban = (company.company_iban or "").replace(" ", "")
    name = (company.company_owner or company.company_name or "").strip()
    amount = f"{Decimal(invoice.invoice_total):.2f}"
    remittance = f"RE {invoice.invoice_no}"

    # EPC069-12 standard
    # Lines:
    # 1: BCD
    # 2: Version (001)
    # 3: Character set (1 = UTF-8)
    # 4: Identification (SCT)
    # 5: BIC (optional but many scanners like it)
    # 6: Name
    # 7: IBAN
    # 8: Amount (EUR)
    # 9: Purpose (optional)
    # 10: Remittance
    # 11: Information (optional)
    lines = [
        "BCD",
        "001",
        "1",
        "SCT",
        bic,
        name,
        iban,
        f"EUR{amount}",
        "",
        remittance,
        "",
    ]
    return "\n".join(lines)


@login_required
def invoice_pdf_reportlab(request, pk: int):
    invoice = get_object_or_404(
        Invoice.objects.select_related("invoice_customer").prefetch_related("items"),
        pk=pk,
    )
    company = Company.objects.first()
    customer = invoice.invoice_customer
    items = invoice.items.all()

    # --- Build PDF ---
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=22 * mm,
        title=f"Invoice {invoice.invoice_no}",
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Small", fontSize=9, leading=11))
    styles.add(ParagraphStyle(name="Right", parent=styles["Normal"], alignment=2))  # 2 = RIGHT
    styles.add(ParagraphStyle(name="H2", parent=styles["Heading2"], spaceAfter=6))

    story = []

    # Header (Company + Invoice meta)
    company_name = (company.company_name if company else "—")
    story.append(Paragraph(company_name, styles["H2"]))
    if company and company.company_address:
        story.append(Paragraph(company.company_address, styles["Normal"]))
    if company and company.company_phone:
        story.append(Paragraph(f"Phone: {company.company_phone}", styles["Normal"]))
    if company and company.company_email:
        story.append(Paragraph(f"Email: {company.company_email}", styles["Normal"]))

    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(f"<b>Invoice:</b> {invoice.invoice_no}", styles["Normal"]))
    story.append(Paragraph(f"<b>Order date:</b> {invoice.invoice_order_date}", styles["Normal"]))
    story.append(Paragraph(f"<b>Service date:</b> {invoice.invoice_service_date}", styles["Normal"]))
    story.append(Spacer(1, 6 * mm))

    # Customer block (rows under each other - no table)
    story.append(Paragraph("<b>Customer</b>", styles["Normal"]))
    story.append(Paragraph(f"Customer number: {customer.customer_number}", styles["Normal"]))
    story.append(Paragraph(f"Name: {customer.customer_name}", styles["Normal"]))
    story.append(Paragraph(f"Address: {customer.customer_address or '—'}", styles["Normal"]))
    story.append(Paragraph(f"Vehicle: {customer.customer_vehicle or '—'}", styles["Normal"]))
    story.append(Paragraph(f"License plate: {customer.customer_license_plate or '—'}", styles["Normal"]))
    story.append(Paragraph(f"Mileage: {customer.customer_kilometers or '—'}", styles["Normal"]))
    story.append(Spacer(1, 6 * mm))

    # Intro text before table
    story.append(Paragraph(
        "Wir bedanken uns für den Auftrag und stellen Ihnen folgende Positionen in Rechnung:",
        styles["Normal"]
    ))
    story.append(Spacer(1, 4 * mm))

    # Items table
    data = [["Diagnosis / Service", "Qty", "Unit (€)", "Total (€)"]]
    for it in items:
        data.append([
            it.invoice_item_diagnosis_text,
            str(it.invoice_item_quantity),
            f"{Decimal(it.invoice_item_unit_price):.2f}",
            f"{Decimal(it.invoice_item_line_total):.2f}",
        ])

    tbl = Table(data, colWidths=[90*mm, 18*mm, 30*mm, 30*mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 6 * mm))

    # Totals (as small table)
    totals = [
        ["Subtotal", f"{Decimal(invoice.invoice_subtotal):.2f} €"],
        [f"VAT ({Decimal(invoice.invoice_vat_percent):.2f}%)", f"{Decimal(invoice.invoice_vat_amount):.2f} €"],
        ["Total", f"{Decimal(invoice.invoice_total):.2f} €"],
    ]
    totals_tbl = Table(totals, colWidths=[60*mm, 35*mm], hAlign="RIGHT")
    totals_tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 2), (-1, 2), colors.lightgrey),
        ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(totals_tbl)

    # Footer + QR (simple approach: add at end)
    story.append(Spacer(1, 10 * mm))

    if company:
        story.append(Paragraph("<b>Bank / Legal</b>", styles["Small"]))
        if company.company_owner:
            story.append(Paragraph(f"Owner: {company.company_owner}", styles["Small"]))
        if company.company_iban:
            story.append(Paragraph(f"IBAN: {company.company_iban}", styles["Small"]))
        if getattr(company, "company_tax_number", None):
            story.append(Paragraph(f"Tax ID: {company.company_tax_number}", styles["Small"]))

        # QR
        try:
            payload = _build_sepa_payload(company, invoice)
            qr_bytes = _make_qr_png_bytes(payload)
            img = Image(BytesIO(qr_bytes), width=30*mm, height=30*mm)
            story.append(Spacer(1, 4 * mm))
            story.append(img)
        except Exception:
            # لو QR فشل لأي سبب لا نوقف PDF
            pass

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="invoice_{invoice.invoice_no}_reportlab.pdf"'
    return response
