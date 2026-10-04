#!/usr/bin/env python3
"""Create a read-only, conservative inventory of title-formatting defects.
No project data is modified by this script.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "title_cleanup_2026-10-04_inventory.json"
SUMMARY = ROOT / "title_cleanup_2026-10-04_inventory_summary.json"

EXT = re.compile(r"(?:\.(?:pdf|docx?|xlsx?|pptx?|zip|rar|7z|mp3|mp4|txt))+(?=\s|$|\()", re.I)
LEADING_CATALOG = re.compile(r"^\s*(?:\d{4,7}\s*[-_–—]\s*|\d{4,7}_)" )
FILE_BOOK = re.compile(r"\s+File\s+كتاب\s+\d+\s*$", re.I)
PDFY = re.compile(r"\s*\(PDFy\s+mirror\)\s*$", re.I)
SHAMELA = re.compile(r"\s+كتاب\s+بصيغة\s+بوك\s+يفتح\s+ب\s+برنامج\s+المكتبة\s+الشاملة\s+انظر\s+للشرح\s+اسفل\s+\d+\s*$")
TRAILING_SOURCE = re.compile(r"\s*(?:[-–—/:]|من)\s*(?:المكتبة\s+القانونية|مكتبة\s+الصديق|قناة\s+الفكر\s+القانوني)\s*$", re.I)
TECH_WORDS = re.compile(r"\b(?:copy|conflicted|compressed|emailing|scan|draft|final|new|version)\b|(?:@[A-Za-z0-9._-]+)", re.I)
ACADEMIC_JOIN = re.compile(r"(?:الأول|الثاني|الثالث|الرابع|الخامس)(?:دكتوراه|ماجستير|رسالة)$")
BAD_DELIMS = re.compile(r"\s*[-_–—]{2,}\s*")
TRAILING_COUNT = re.compile(r"\s+\d{1,4}\s*$")
ARABIC_WORD = re.compile(r"[\u0600-\u06FF]")

EXPLICIT = {
    "rasail_16191": "بحث الوادعي — رسالة ماجستير، المعهد العالي للقضاء",
    "legal_lib_13376": "بحث الوادعي — رسالة ماجستير، المعهد العالي للقضاء",
    "risail_34829": "بحث الوادعي — رسالة ماجستير، المعهد العالي للقضاء",
    "rasail_17451": "الحسبة والسياسة الجنائية — الجزء الأول",
    "rasail_17452": "الحسبة والسياسة الجنائية — الجزء الثاني",
    "rasail_15188": "الحسبة والسياسة الجنائية",
    "risail_19720": "الحسبة والسياسة الجنائية",
    "qadaa_10189": "الحسبة والسياسة الجنائية — سعد العريفي",
}


def clean(title: str) -> tuple[str, list[str]]:
    original = title or ""
    value = original.replace("\u00a0", " ").replace("_", " ")
    reasons: list[str] = []
    if value != original:
        reasons.append("استبدال فواصل اسم الملف")
    new = LEADING_CATALOG.sub("", value)
    if new != value:
        value = new; reasons.append("حذف رقم فهرسة تقني")
    new = PDFY.sub("", value)
    if new != value:
        value = new; reasons.append("حذف لاحقة أرشيفية")
    new = FILE_BOOK.sub("", value)
    if new != value:
        value = new; reasons.append("حذف وسم ملف أرشيفي")
    new = SHAMELA.sub("", value)
    if new != value:
        value = new; reasons.append("حذف وصف تشغيل تقني")
    new = EXT.sub("", value)
    if new != value:
        value = new; reasons.append("حذف امتداد ملف")
    new = TRAILING_SOURCE.sub("", value)
    if new != value:
        value = new; reasons.append("حذف إحالة مصدر مكررة")
    new = BAD_DELIMS.sub(" — ", value)
    if new != value:
        value = new; reasons.append("توحيد الفواصل")
    value = re.sub(r"\s+", " ", value).strip(" -–—_./:؛،")
    return value, reasons


def reason_for(title: str, proposed: str, reasons: list[str]) -> list[str]:
    flags = list(reasons)
    if TECH_WORDS.search(title): flags.append("ضوضاء تقنية أو اسم نسخ")
    if ACADEMIC_JOIN.search(title): flags.append("التصاق بيانات الرسالة بالعنوان")
    if len(title) > 180: flags.append("عنوان طويل يحوي بيانات وصفية")
    if re.search(r"\s{2,}", title): flags.append("مسافات زائدة")
    if not flags and proposed != title: flags.append("تنسيق عنوان")
    return sorted(set(flags))


def is_safe(original: str, proposed: str, flags: list[str], item: dict) -> bool:
    # Automatic changes may only remove clearly technical/archive presentation noise.
    if item["id"] in EXPLICIT:
        return True
    if not proposed or len(proposed) < 4:
        return False
    if "ضوضاء تقنية أو اسم نسخ" in flags or "عنوان طويل يحوي بيانات وصفية" in flags or "التصاق بيانات الرسالة بالعنوان" in flags:
        return False
    if len(proposed) > len(original) + 10:
        return False
    return bool(flags)


def main() -> None:
    items = json.load(open(ROOT / "items.json", encoding="utf-8"))
    rows = []
    for item in items:
        title = str(item.get("title") or "").strip()
        proposed, reasons = clean(title)
        if item.get("source") == "أرشيف الإنترنت":
            without_archive_serial = re.sub(r"^(?:0\d{3,6}|[1-9]\d{4,6})\s+", "", proposed)
            if without_archive_serial != proposed:
                proposed = without_archive_serial
                reasons.append("حذف رقم فهرسة أرشيفي")
        if item["id"] in EXPLICIT:
            proposed = EXPLICIT[item["id"]]
            reasons = ["تصحيح تحريري محدد لعنوان ظاهر غير مناسب"]
        flags = reason_for(title, proposed, reasons)
        if not flags or proposed == title:
            continue
        rows.append({
            "id": item["id"],
            "title": title,
            "proposed_title": proposed,
            "source": item.get("source", ""),
            "author": item.get("author", ""),
            "category": item.get("category", ""),
            "material_type": item.get("material_type", ""),
            "file_type": item.get("file_type", ""),
            "reasons": flags,
            "safe_auto": is_safe(title, proposed, flags, item),
        })
    rows.sort(key=lambda x: (not x["safe_auto"], x["id"]))
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {
        "total_items": len(items),
        "candidates": len(rows),
        "safe_auto": sum(x["safe_auto"] for x in rows),
        "semantic_review": sum(not x["safe_auto"] for x in rows),
        "by_reason": Counter(reason for x in rows for reason in x["reasons"]),
        "by_source": Counter(x["source"] for x in rows),
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
