#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###############################################################################
##### fix_po.py path/to/ar.po [--keep-fuzzy]###################################
###############################################################################
# fix_po.py [-h] [--remove-fuzzy] [--fix-wrong] [--force] po_file
###############################################################################
# python3 fix_po_de.py de/LC_MESSAGES/django.po --remove-fuzzy --fix-wrong --force
#
# python3 fix_po_ar.py ar/LC_MESSAGES/django.po --remove-fuzzy --fix-wrong --force
#
# python3 fix_po_tr.py tr/LC_MESSAGES/django.po --remove-fuzzy --fix-wrong --force
###############################################################################
###############################################################################

# How to use

# 1) Only fill empty msgstr (safe):

# python3 fix_po.py django.po --lang de

# 2) Fill empty msgstr + remove fuzzy markers:

# python3 fix_po.py django.po --lang de/LC_MESSAGES/django.po --remove-fuzzy

# 3) Also fix known wrong translations (recommended for your file):

# python3 fix_po.py de/LC_MESSAGES/django.po --lang de --remove-fuzzy --fix-wrong

#############################################################################

"""
fix_po.py — safe PO fixer (German example)

Behavior:
- Input: path/to/django.po
- Renames original to: path/to/django.before_fixing.po
- Writes fixed file to: path/to/django.po

Preserves:
- ALL lines and ordering (including #:, # comments, fuzzy comments, etc.)
- msgids unchanged

Options:
- --remove-fuzzy : remove '#, fuzzy' and '#| msgid ...' hint lines
- --fix-wrong    : fix known wrong translations (only when current msgstr matches known bad value exactly)
- --force        : overwrite existing django.before_fixing.po if it exists
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple


# ---------- CONFIG: German fills for empty msgstr ----------
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
}

MULTILINE_MSGID = (
    "An unexpected server error occurred. Please try again later or contact the "
    "administrator if the problem persists."
)
FILL_MAP_DE[MULTILINE_MSGID] = (
    "Ein unerwarteter Serverfehler ist aufgetreten. Bitte versuchen Sie es später erneut "
    "oder kontaktieren Sie den Administrator, falls das Problem weiterhin besteht."
)

# ---------- CONFIG: Known wrong translations to fix (opt-in) ----------
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


# ---------- PO parsing helpers ----------
def parse_po_into_blocks(text: str) -> List[str]:
    return re.split(r"\n{2,}", text)


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


def fix_po(text: str, remove_fuzzy_flag: bool, fix_wrong: bool) -> str:
    blocks = parse_po_into_blocks(text)
    fixed_blocks: List[str] = []

    for blk in blocks:
        b = blk

        if "msgid" in b and "msgstr" in b:
            msgid = extract_msgid(b)

            if remove_fuzzy_flag:
                b = remove_fuzzy(b)

            if has_empty_msgstr(b) and msgid in FILL_MAP_DE:
                b = set_msgstr_single_line(b, FILL_MAP_DE[msgid])

            if fix_wrong:
                current = get_msgstr(b)
                key = (msgid, current)
                if key in FIX_WRONG_DE:
                    b = set_msgstr_single_line(b, FIX_WRONG_DE[key])

        fixed_blocks.append(b)

    return "\n\n".join([blk.rstrip("\n") for blk in fixed_blocks]).rstrip() + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("po_file", type=Path, help="Path to django.po")
    ap.add_argument("--remove-fuzzy", action="store_true", help="Remove '#, fuzzy' and '#| msgid ...' lines")
    ap.add_argument("--fix-wrong", action="store_true", help="Fix known wrong translations (opt-in)")
    ap.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing django.before_fixing.po if it exists",
    )
    args = ap.parse_args()

    src: Path = args.po_file
    if src.name != "django.po":
        raise SystemExit("Please pass the path to django.po (the script renames it to django.before_fixing.po).")

    backup = src.with_name("django.before_fixing.po")

    if backup.exists():
        if args.force:
            backup.unlink()
        else:
            raise SystemExit(f"Backup already exists: {backup}. Use --force to overwrite it.")

    # Read original content
    original_text = src.read_text(encoding="utf-8")

    # Produce fixed text
    fixed_text = fix_po(
        text=original_text,
        remove_fuzzy_flag=args.remove_fuzzy,
        fix_wrong=args.fix_wrong,
    )

    # Rename original -> backup
    src.rename(backup)

    # Write fixed file to original path
    src.write_text(fixed_text, encoding="utf-8")

    print(f"Backup created: {backup}")
    print(f"Fixed file written: {src}")


if __name__ == "__main__":
    main()