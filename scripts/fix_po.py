#!/usr/bin/env python3
# scripts/fix_po.py
#
# Removes "fuzzy" flags and fixes known msgid->msgstr translations
# for de/ar locale files.

############ To Run ##############
# python scripts/fix_po.py locale/ar/LC_MESSAGES/django.po ar
# python scripts/fix_po.py locale/de/LC_MESSAGES/django.po de

# django-admin compilemessages



from __future__ import annotations
import re
import sys
from pathlib import Path


AR_MAP = {
    "Company name": "اسم الشركة",
    "Company address": "عنوان الشركة",
    "Company phone": "هاتف الشركة",
    "Company email": "البريد الإلكتروني للشركة",
    "Company website": "موقع الشركة الإلكتروني",
    "Company owner": "مالك الشركة",
    "Company IBAN": "رقم الآيبان للشركة",
    "Company tax number": "الرقم الضريبي للشركة",

    "User": "المستخدم",
    "Role": "الدور",
    "Photo": "صورة",
    "Profile": "الملف الشخصي",

    "Customer number": "رقم العميل",
    "Customer name": "اسم العميل",
    "Customer address": "عنوان العميل",
    "Vehicle": "المركبة",
    "License plate number": "رقم اللوحة",
    "Mileage": "عداد الكيلومترات",

    "Diagnosis title": "عنوان التشخيص",
    "Default price (€)": "السعر الافتراضي (€)",
    "Diagnosis": "تشخيص",
    "Diagnoses": "التشخيصات",

    "VAT (%)": "ضريبة القيمة المضافة (%)",
    "VAT amount": "قيمة ضريبة القيمة المضافة",
    "Created by": "أُنشِئت بواسطة",
    "Notes": "ملاحظات",

    "Invoice item": "بند فاتورة",
    "Invoice items": "بنود الفاتورة",
    "Position": "الترتيب",

    "Select diagnosis from predefined list": "اختر التشخيص من القائمة المحددة مسبقًا",
    "Diagnosis text (snapshot)": "نص التشخيص (نسخة محفوظة)",

    "Unit price (€)": "سعر الوحدة (€)",
    "Line total (€)": "إجمالي السطر (€)",

    "Select invoice": "اختر فاتورة",
    "Enter new invoice number": "أدخل رقم فاتورة جديد",

    "Select Customer": "اختر العميل",
    "Choose customer...": "اختر عميلًا...",

    "Order": "الطلب",
    "Service": "الخدمة",
    "VAT": "ضريبة القيمة المضافة",
}

DE_MAP = {
    "Company owner": "Inhaber",
    "Company IBAN": "IBAN",
    "Company tax number": "Steuernummer",

    "Profile": "Profil",

    "Customer number": "Kundennummer",
    "Customer name": "Kundenname",
    "Customer address": "Kundenadresse",
    "Vehicle": "Fahrzeug",
    "License plate number": "Kennzeichen",
    "Mileage": "Kilometerstand",

    "Diagnosis title": "Diagnosetitel",
    "Default price (€)": "Standardpreis (€)",
    "Diagnosis": "Diagnose",
    "Diagnoses": "Diagnosen",

    "VAT (%)": "MwSt. (%)",
    "VAT amount": "MwSt.-Betrag",
    "Created by": "Erstellt von",
    "Notes": "Notizen",

    "Invoice": "Rechnung",
    "Position": "Position",
    "Unit price (€)": "Stückpreis (€)",
    "Line total (€)": "Zeilensumme (€)",
    "Invoice item": "Rechnungsposition",
    "Invoice items": "Rechnungspositionen",

    "Select invoice": "Rechnung auswählen",
    "Enter new invoice number": "Neue Rechnungsnummer eingeben",

    "Select Customer": "Kunde auswählen",
    "Choose customer...": "Kunde wählen...",

    "Order": "Bestellung",
    "Service": "Service",
    "VAT": "MwSt.",
}


def fix_po(path: Path, lang: str) -> None:
    mapping = AR_MAP if lang == "ar" else DE_MAP if lang == "de" else None
    if mapping is None:
        raise SystemExit(f"Unsupported lang '{lang}'. Use ar or de.")

    lines = path.read_text(encoding="utf-8").splitlines()

    out: list[str] = []
    entry: list[str] = []

    def flush(entry_lines: list[str]) -> None:
        if not entry_lines:
            return

        # Extract msgid (single-line msgid assumed; ok for your file style)
        msgid = None
        msgstr_idx = None

        for i, l in enumerate(entry_lines):
            if l.startswith("msgid "):
                m = re.match(r'msgid "(.*)"', l)
                msgid = m.group(1) if m else ""
                break

        # Replace msgstr if we have a mapping (skip header msgid "")
        if msgid is not None and msgid != "":
            for j, l in enumerate(entry_lines):
                if l.startswith("msgstr "):
                    msgstr_idx = j
                    break
            if msgstr_idx is not None and msgid in mapping:
                entry_lines[msgstr_idx] = f'msgstr "{mapping[msgid]}"'

        # Remove fuzzy flags and old msgid references (#| msgid ...)
        cleaned: list[str] = []
        for l in entry_lines:
            if l.startswith("#,"):
                flags = [f.strip() for f in l[2:].split(",")]
                flags = [f for f in flags if f != "fuzzy"]
                if flags:
                    cleaned.append("#, " + ", ".join(flags))
                continue
            if l.startswith("#|"):
                continue
            cleaned.append(l)

        out.extend(cleaned)

    for l in lines:
        if l.strip() == "":
            flush(entry)
            out.append("")
            entry = []
        else:
            entry.append(l)

    flush(entry)

    path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python scripts/fix_po.py <path-to-django.po> <lang: ar|de>")

    fix_po(Path(sys.argv[1]), sys.argv[2])
    print("OK: fixed", sys.argv[1])
