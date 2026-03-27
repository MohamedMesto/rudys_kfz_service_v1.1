#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
fix_po.py — safe PO fixer (de/ar/tr)

Behavior:
- Input: path/to/django.po
- Renames original to: path/to/django.before_fixing.po
- Writes fixed file to: path/to/django.po

Preserves:
- ALL lines and ordering (including #:, # comments, etc.)
- msgids unchanged (EXCEPT optional normalization with --normalize-best-regards)

Options:
- --remove-fuzzy : remove '#, fuzzy' and '#| msgid ...' hint lines
- --fix-wrong    : fix known wrong translations (only when current msgstr matches known bad value exactly)
- --fill-empty   : fill empty msgstr "" for known keys (enabled by default; use --no-fill-empty to disable)
- --normalize-best-regards : map "Best Regards." -> "Best Regards" by copying translation (does not delete old entry)
- --force        : overwrite existing django.before_fixing.po if it exists

Usage examples:
  python3 fix_po.py de/LC_MESSAGES/django.po --remove-fuzzy --fix-wrong --force
  python3 fix_po.py ar/LC_MESSAGES/django.po --remove-fuzzy --fill-empty --force
  python3 fix_po.py tr/LC_MESSAGES/django.po --remove-fuzzy --fix-wrong --force
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional


# ---------------------------------------------------------------------------
# Translation maps
# ---------------------------------------------------------------------------

# German
FILL_MAP_DE: Dict[str, str] = {
    "BIC": "BIC",
    "Admin": "Administrator",
    "Mechanic": "Mechaniker",
    "Accountant": "Buchhalter",
    "Manage Users": "Benutzer verwalten",
    "Password confirmation": "Passwortbestätigung",
    "The page you requested was not found.": "Die angeforderte Seite wurde nicht gefunden.",
    "Server Error": "Serverfehler",
    "Something went wrong.": "Etwas ist schiefgelaufen.",
    "Back to home": "Zurück zur Startseite",
    "Back to Homepage": "Zurück zur Startseite",
    "Admin dashboard": "Administrator-Dashboard",
    "Best Regards": "Mit freundlichen Grüßen",
}
MULTILINE_MSGID = (
    "An unexpected server error occurred. Please try again later or contact the "
    "administrator if the problem persists."
)
FILL_MAP_DE[MULTILINE_MSGID] = (
    "Ein unerwarteter Serverfehler ist aufgetreten. Bitte versuchen Sie es später erneut "
    "oder kontaktieren Sie den Administrator, falls das Problem weiterhin besteht."
)
FIX_WRONG_DE: Dict[Tuple[str, str], str] = {
    ("Order Date", "Auftragsnummer"): "Auftragsdatum",
    ("Order date", "Auftragsnummer"): "Auftragsdatum",
    ("Photo", "Handynummer"): "Foto",
    ("Company phone", "Firma Phone"): "Telefon (Firma)",
    ("Company email", "Firma Email"): "E-Mail (Firma)",
    ("Company website", "Firma Webseite"): "Webseite (Firma)",
    ("Custom diagnosis text", "Diagnosetitel"): "Benutzerdefinierter Diagnosetext",
    ("Unit price", "Einzelpreis "): "Einzelpreis",
    ("Company name", "Firmenname:"): "Firmenname",
    ("Company address", "Firmenadresse:"): "Firmenadresse",
}

# Arabic
FILL_MAP_AR: Dict[str, str] = {
    "Email": "البريد الإلكتروني",
    "Username": "اسم المستخدم",
    "Password": "كلمة المرور",
    "Company": "الشركة",
    "Companies": "الشركات",
    "Admin": "مسؤول",
    "Mechanic": "ميكانيكي",
    "Accountant": "محاسب",
    "User": "المستخدم",
    "Role": "الدور",
    "Phone": "الهاتف",
    "Address": "العنوان",
    "Photo": "صورة",
    "Profile": "الملف الشخصي",
    "Profiles": "الملفات الشخصية",
    "Customer": "العميل",
    "Customers": "العملاء",
    "Invoice": "فاتورة",
    "Invoices": "الفواتير",
    "Subtotal": "المجموع الفرعي",
    "VAT": "ضريبة القيمة المضافة",
    "Total": "الإجمالي",
    "Owner": "المالك",
    "Tax ID": "الرقم الضريبي",
    "Best Regards": "مع أطيب التحيات",
    "Best Regards.": "مع أطيب التحيات",
    "Page not found": "الصفحة غير موجودة",
    "The page you requested was not found.": "الصفحة التي طلبتها غير موجودة.",
    "Back to home": "العودة إلى الصفحة الرئيسية",
    "Server Error": "خطأ في الخادم",
    "Something went wrong.": "حدث خطأ ما.",
    "Back to Homepage": "العودة إلى الصفحة الرئيسية",
    "We thank you for your order and invoice the following items.": "نشكركم على طلبكم ونُدرج لكم البنود التالية في هذه الفاتورة.",
}
FILL_MAP_AR[MULTILINE_MSGID] = (
    "حدث خطأ غير متوقع في الخادم. يرجى المحاولة لاحقًا أو التواصل مع المسؤول إذا استمرت المشكلة."
)
FIX_WRONG_AR: Dict[Tuple[str, str], str] = {
    # If you ever find German/Turkish leaked into Arabic, add pairs here.
}

# Turkish
FILL_MAP_TR: Dict[str, str] = {
    "The page you requested was not found.": "İstediğiniz sayfa bulunamadı.",
    "Server Error": "Sunucu Hatası",
    "Something went wrong.": "Bir şeyler ters gitti.",
    "Back to home": "Ana sayfaya dön",
    "Back to Homepage": "Ana sayfaya dön",
    "Best Regards": "Saygılarımızla",
    "Best Regards.": "Saygılarımızla",
}
FILL_MAP_TR[MULTILINE_MSGID] = (
    "Beklenmeyen bir sunucu hatası oluştu. Lütfen daha sonra tekrar deneyin veya "
    "sorun devam ederse yöneticiyle iletişime geçin."
)
FIX_WRONG_TR: Dict[Tuple[str, str], str] = {
    ("The page you requested was not found.", "Die angeforderte Seite wurde nicht gefunden."): "İstediğiniz sayfa bulunamadı.",
    ("Server Error", "Serverfehler"): "Sunucu Hatası",
    ("Something went wrong.", "Etwas ist schiefgelaufen."): "Bir şeyler ters gitti.",
    ("Page not found", "Servis bulunamadı."): "Sayfa bulunamadı.",
    ("Back to home", "Girişe dön"): "Ana sayfaya dön",
    ("Back to Homepage", "Girişe dön"): "Ana sayfaya dön",
}

LANG_MAP = {
    "de": (FILL_MAP_DE, FIX_WRONG_DE),
    "ar": (FILL_MAP_AR, FIX_WRONG_AR),
    "tr": (FILL_MAP_TR, FIX_WRONG_TR),
}


# ---------------------------------------------------------------------------
# PO parsing helpers (preserve blocks)
# ---------------------------------------------------------------------------

def parse_po_into_blocks(text: str) -> List[str]:
    return re.split(r"\n{2,}", text)


def detect_language_from_header(text: str) -> Optional[str]:
    # Look for:  "Language: ar\n"
    m = re.search(r'^\s*"Language:\s*([a-zA-Z_@-]+)\\n"\s*$', text, flags=re.M)
    if m:
        return m.group(1).split("_")[0].lower()
    # Sometimes header has: Language: ar (not quoted) in custom files
    m2 = re.search(r"^Language:\s*([a-zA-Z_@-]+)\s*$", text, flags=re.M)
    if m2:
        return m2.group(1).split("_")[0].lower()
    return None


def extract_msgid(block: str) -> str:
    b = "\n" + block + "\n"

    m = re.search(r'\nmsgid\s+"(.*?)"\nmsgstr', b, flags=re.S)
    if m:
        msgid_part = m.group(1)
        if msgid_part != "":
            return msgid_part

    m2 = re.search(r'\nmsgid\s+""\n((?:"(?:[^"\\]|\\.)*"\n)+)\s*msgstr', b, flags=re.S)
    if m2:
        quoted_lines = m2.group(1).splitlines()
        s = "".join([line.strip()[1:-1] for line in quoted_lines if line.strip().startswith('"')])
        s = s.replace(r"\\", "\\").replace(r"\"", '"')
        return s

    return ""


def has_empty_msgstr(block: str) -> bool:
    b = "\n" + block + "\n"
    return bool(re.search(r'\nmsgstr\s+""\s*(?:\n"(?:[^"\\]|\\.)*")*\s*\n', b))


def get_msgstr(block: str) -> str:
    b = "\n" + block + "\n"

    m = re.search(r'\nmsgstr\s+"(.*?)"\s*(?:\n|$)', b, flags=re.S)
    if not m:
        return ""
    first = m.group(1)

    if first == "":
        m2 = re.search(r'\nmsgstr\s+""\n((?:"(?:[^"\\]|\\.)*"\n)+)', b, flags=re.S)
        if m2:
            quoted_lines = m2.group(1).splitlines()
            s = "".join([line.strip()[1:-1] for line in quoted_lines if line.strip().startswith('"')])
            s = s.replace(r"\\", "\\").replace(r"\"", '"')
            return s
        return ""

    m3 = re.search(r'\nmsgstr\s+"(?:[^"\\]|\\.)*"\n((?:"(?:[^"\\]|\\.)*"\n)+)', b, flags=re.S)
    if m3:
        extra_lines = m3.group(1).splitlines()
        extra = "".join([line.strip()[1:-1] for line in extra_lines if line.strip().startswith('"')])
        extra = extra.replace(r"\\", "\\").replace(r"\"", '"')
        return first.replace(r"\\", "\\").replace(r"\"", '"') + extra

    return first.replace(r"\\", "\\").replace(r"\"", '"')


def set_msgstr_single_line(block: str, new_str: str) -> str:
    esc = new_str.replace("\\", r"\\").replace('"', r"\"")
    pattern = r'\nmsgstr\s+".*?"(?:\n"(?:[^"\\]|\\.)*")*'
    repl = f'\nmsgstr "{esc}"'
    b = "\n" + block + "\n"
    b2 = re.sub(pattern, repl, b, flags=re.S)
    return b2.strip("\n")


def remove_fuzzy(block: str) -> str:
    lines = block.splitlines(True)
    out = []
    for line in lines:
        if re.match(r"^\s*#,\s*fuzzy\s*$", line.strip()):
            continue
        if re.match(r"^\s*#\|\s*msgid\s+", line):
            continue
        out.append(line)
    return "".join(out).rstrip("\n")


def normalize_best_regards(blocks: List[str]) -> List[str]:
    """
    If file contains 'Best Regards.' and 'Best Regards', copy translation from one to the other
    when the target is empty.
    Does NOT delete any entry (safe).
    """
    def find_block(msgid: str) -> Optional[int]:
        for i, b in enumerate(blocks):
            if "msgid" in b and "msgstr" in b and extract_msgid(b) == msgid:
                return i
        return None

    i_plain = find_block("Best Regards")
    i_dot = find_block("Best Regards.")

    if i_plain is None or i_dot is None:
        return blocks

    plain = blocks[i_plain]
    dot = blocks[i_dot]

    plain_str = get_msgstr(plain)
    dot_str = get_msgstr(dot)

    # If one is empty but the other has text, fill the empty one
    if (plain_str.strip() == "") and (dot_str.strip() != ""):
        blocks[i_plain] = set_msgstr_single_line(plain, dot_str)
    elif (dot_str.strip() == "") and (plain_str.strip() != ""):
        blocks[i_dot] = set_msgstr_single_line(dot, plain_str)

    return blocks


def fix_po(text: str, lang: str, remove_fuzzy_flag: bool, fix_wrong: bool, fill_empty: bool,
           normalize_br: bool) -> str:
    blocks = parse_po_into_blocks(text)

    fill_map, fix_wrong_map = LANG_MAP.get(lang, ({}, {}))

    fixed_blocks: List[str] = []
    for blk in blocks:
        b = blk

        if "msgid" in b and "msgstr" in b:
            msgid = extract_msgid(b)

            if remove_fuzzy_flag:
                b = remove_fuzzy(b)

            if fill_empty and has_empty_msgstr(b) and msgid in fill_map:
                b = set_msgstr_single_line(b, fill_map[msgid])

            if fix_wrong:
                current = get_msgstr(b)
                key = (msgid, current)
                if key in fix_wrong_map:
                    b = set_msgstr_single_line(b, fix_wrong_map[key])

        fixed_blocks.append(b)

    if normalize_br:
        fixed_blocks = normalize_best_regards(fixed_blocks)

    return "\n\n".join([blk.rstrip("\n") for blk in fixed_blocks]).rstrip() + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("po_file", type=Path, help="Path to django.po")
    ap.add_argument("--remove-fuzzy", action="store_true", help="Remove '#, fuzzy' and '#| msgid ...' lines")
    ap.add_argument("--fix-wrong", action="store_true", help="Fix known wrong translations (opt-in)")
    ap.add_argument("--fill-empty", action="store_true", default=True, help="Fill empty msgstr for known keys (default ON)")
    ap.add_argument("--no-fill-empty", action="store_true", help="Disable filling empty msgstr")
    ap.add_argument("--normalize-best-regards", action="store_true", help='Sync translations for "Best Regards" and "Best Regards."')
    ap.add_argument("--force", action="store_true", help="Overwrite existing django.before_fixing.po if it exists")
    args = ap.parse_args()

    src: Path = args.po_file
    if src.name != "django.po":
        raise SystemExit("Please pass the path to django.po (it will be renamed to django.before_fixing.po).")

    backup = src.with_name("django.before_fixing.po")
    if backup.exists():
        if args.force:
            backup.unlink()
        else:
            raise SystemExit(f"Backup already exists: {backup}. Use --force to overwrite it.")

    original_text = src.read_text(encoding="utf-8")
    lang = detect_language_from_header(original_text) or "en"
    if lang not in LANG_MAP:
        raise SystemExit(f"Unsupported or missing Language in header: '{lang}'. Supported: {', '.join(LANG_MAP.keys())}")

    fill_empty = False if args.no_fill_empty else True

    fixed_text = fix_po(
        text=original_text,
        lang=lang,
        remove_fuzzy_flag=args.remove_fuzzy,
        fix_wrong=args.fix_wrong,
        fill_empty=fill_empty,
        normalize_br=args.normalize_best_regards,
    )

    # Rename original -> backup
    src.rename(backup)

    # Write fixed file to original path
    src.write_text(fixed_text, encoding="utf-8")

    print(f"Detected language: {lang}")
    print(f"Backup created: {backup}")
    print(f"Fixed file written: {src}")


if __name__ == "__main__":
    main()