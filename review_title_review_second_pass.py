#!/usr/bin/env python3
"""الجولة الثانية للحالات الملتبسة فقط؛ لا تعدّل items.json ولا أي بيانات منشورة."""

from __future__ import annotations

import concurrent.futures
import json
import os
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
ITEMS_PATH = ROOT / "items.json"
REVIEW_PATH = ROOT / "title_review_needed.json"
PROGRESS_PATH = ROOT / "title_review_second_pass.progress.json"
OUTPUT_PATH = ROOT / "title_review_second_pass.json"
MODEL = "gpt-5-mini"
BATCH_SIZE = 75
MAX_WORKERS = 8
MAX_RETRIES = 4


def load_cases() -> list[dict]:
    items = {str(item["id"]): item for item in json.loads(ITEMS_PATH.read_text(encoding="utf-8"))}
    queue = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
    cases = []
    for prior in queue:
        item = items.get(str(prior["id"]))
        if not item:
            raise ValueError(f"حالة REVIEW غير موجودة في البيانات الحالية: {prior['id']}")
        cases.append({
            "id": str(item["id"]),
            "title": item.get("title", ""),
            "author": item.get("author", ""),
            "investigator": item.get("investigator", ""),
            "publisher": item.get("publisher", ""),
            "year": item.get("year", ""),
            "source": item.get("source", ""),
            "category": item.get("category", ""),
            "material_type": item.get("material_type", ""),
            "file_type": item.get("file_type", ""),
            "pages_count": item.get("pages_count", ""),
            "file_size": item.get("file_size", ""),
            "link_telegram": item.get("link_telegram", ""),
            "link_direct": item.get("link_direct", ""),
            "link_drive": item.get("link_drive", ""),
            "previous_reason": prior.get("reason", ""),
        })
    return cases


def batch_payload(batch: list[dict]) -> dict:
    prompt = f"""أنت المراجع الثاني لمكنز القضاء والأنظمة والمحاماة. افصل الحالات الملتبسة باستخدام **كل الحقول المتاحة** لكل سجل: العنوان، المؤلف، المحقق، الناشر، السنة، المصدر، التصنيف السابق، نوع المادة والملف، عدد الصفحات، والروابط أو معرفات الصفحة إن وجدت. المصدر والتصنيف السابق قرينتان فقط ولا يكفيان وحدهما.

القرار:
- KEEP: عندما توجد صلة حقيقية بالقضاء أو الأنظمة أو القانون أو المحاماة أو التحكيم أو الإثبات أو الجنايات أو الأحوال الشخصية أو المعاملات القانونية. يشمل ذلك التراث الفقهي والقضائي والتاريخ القضائي متى كان الموضوع القضائي حقيقياً.
- REMOVE: فقط عند وضوح الخروج عن النطاق من البيانات، مثل العبادات المحضة، العقيدة والحديث واللغة والأدب والعلوم والتاريخ العام أو السياسة العامة بلا صلة قانونية حقيقية، أو الألفاظ المشتركة مثل قضاء الصلاة/القدر/القضاء على/محكمة التاريخ.
- REVIEW: فقط إذا تعذر الحسم بعد كل الحقول. لا تستخدم REVIEW لمجرد أن المادة تراثية أو فقهية قضائية.

لا تكفي ألفاظ حكم أو قضاء أو محاكمة أو حقوق أو نظام أو شهادة أو دعوى وحدها. اكتب سبباً عربياً موجزاً يذكر الدليل الحاسم من الحقول المتاحة.

السجلات:
{json.dumps(batch, ensure_ascii=False)}"""
    return {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "أنت مراجع قانوني علمي دقيق. أخرج JSON مطابقاً للمخطط فقط."},
            {"role": "user", "content": prompt},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "second_review_decisions",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "decision": {"type": "string", "enum": ["KEEP", "REMOVE", "REVIEW"]},
                                    "reason": {"type": "string"},
                                    "confidence": {"type": "number"},
                                },
                                "required": ["id", "decision", "reason", "confidence"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["items"],
                    "additionalProperties": False,
                },
            },
        },
        "max_completion_tokens": 7000,
    }


def classify(batch: list[dict]) -> list[dict]:
    expected = {row["id"] for row in batch}
    error = ""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                f"{os.environ['OPENAI_API_BASE'].rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}", "Content-Type": "application/json"},
                json=batch_payload(batch), timeout=240,
            )
            response.raise_for_status()
            rows = json.loads(response.json()["choices"][0]["message"]["content"])["items"]
            if len(rows) != len(batch) or {str(row.get("id")) for row in rows} != expected:
                raise ValueError("مخرجات الدفعة لا تطابق السجلات")
            return [{
                "id": str(row["id"]),
                "decision": row["decision"],
                "reason": str(row["reason"])[:240],
                "confidence": max(0, min(1, float(row["confidence"]))),
            } for row in rows]
        except Exception as exc:
            error = str(exc)
            time.sleep(min(2 ** attempt, 12))
    return [{"id": row["id"], "decision": "REVIEW", "reason": f"تعذر الحسم التقني: {error[:120]}", "confidence": 0.0} for row in batch]


def load_progress() -> dict[str, dict]:
    for file in (PROGRESS_PATH, OUTPUT_PATH):
        if file.exists():
            return {str(row["id"]): row for row in json.loads(file.read_text(encoding="utf-8")).get("decisions", [])}
    return {}


def save(rows: dict[str, dict], total: int, final: bool = False) -> None:
    payload = {"model": MODEL, "total_cases": total, "decisions": list(rows.values())}
    (OUTPUT_PATH if final else PROGRESS_PATH).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    cases = load_cases()
    prior = {case["id"]: case for case in cases}
    rows = load_progress()
    pending = [case for case in cases if case["id"] not in rows]
    batches = [pending[i:i + BATCH_SIZE] for i in range(0, len(pending), BATCH_SIZE)]
    print(f"حالات الجولة الثانية: {len(cases)} | منجزة: {len(rows)} | متبقية: {len(pending)}", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(classify, batch) for batch in batches]
        for number, future in enumerate(concurrent.futures.as_completed(futures), 1):
            for decision in future.result():
                context = prior[decision["id"]]
                rows[decision["id"]] = {**decision, "context": context}
            save(rows, len(cases))
            print(f"راجعت الدفعة {number}/{len(batches)} | محفوظ: {len(rows)}", flush=True)
    save(rows, len(cases), final=True)
    if PROGRESS_PATH.exists():
        PROGRESS_PATH.unlink()
    print(f"اكتملت الجولة الثانية: {len(rows)} حالة", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
