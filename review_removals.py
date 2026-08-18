#!/usr/bin/env python3
"""مراجعة مستقلة محافظة لمرشحي الحذف.

لا تثبت REMOVE إلا إذا كان خروج العنوان عن نطاق المكنز واضحاً. لا يغيّر items.json.
"""

from __future__ import annotations

import concurrent.futures
import json
import os
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
ITEMS_PATH = ROOT / "items.json"
CLASSIFICATIONS_PATH = ROOT / "title_classifications.json"
OUTPUT_PATH = ROOT / "title_removal_review.json"
PROGRESS_PATH = ROOT / "title_removal_review.progress.json"
MODEL = "gpt-5-mini"
BATCH_SIZE = 100
MAX_WORKERS = 8
MAX_RETRIES = 4


def make_payload(batch: list[dict]) -> dict:
    rows = [{"id": str(item["id"]), "title": str(item.get("title", "")).strip()} for item in batch]
    prompt = f"""أنت قاضٍ مراجع شديد التحفظ لمكنز القضاء والأنظمة والمحاماة. راجع مرشحي الحذف التاليين اعتماداً على العنوان كاملاً فقط.

ثبت REMOVE فقط عندما يكون موضوع العنوان واضحاً أنه خارج القضاء والأنظمة والقانون والمحاماة والجنايات والإثبات والعقود القانونية والأحوال الشخصية القضائية والتحكيم والوساطة والحسبة والمظالم.

إذا احتمل العنوان موضوعاً قانونياً أو قضائياً، أو كان مختصراً أو غامضاً، اختر REVIEW. إذا بدا قانونياً أو قضائياً مباشراً رغم التصنيف الأولي فاختر KEEP.

لا تعتمد على المصدر أو التصنيف. لا تحذف بسبب وجود كلمة قضاء أو قانون بمعنى غير واضح. اكتب سبباً عربياً موجزاً لا يتجاوز 12 كلمة.

المرشحون:
{json.dumps(rows, ensure_ascii=False)}"""
    return {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "أنت مراجع محتوى دقيق. أخرج JSON مطابقاً للمخطط فقط."},
            {"role": "user", "content": prompt},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "removal_confirmation",
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
                                    "final_decision": {"type": "string", "enum": ["REMOVE", "REVIEW", "KEEP"]},
                                    "reason": {"type": "string"},
                                    "confidence": {"type": "number"},
                                },
                                "required": ["id", "final_decision", "reason", "confidence"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["items"],
                    "additionalProperties": False,
                },
            },
        },
        "max_completion_tokens": 6000,
    }


def review_batch(batch: list[dict]) -> list[dict]:
    api_base = os.environ["OPENAI_API_BASE"].rstrip("/")
    api_key = os.environ["OPENAI_API_KEY"]
    expected = {str(item["id"]) for item in batch}
    error = ""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                f"{api_base}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=make_payload(batch),
                timeout=240,
            )
            response.raise_for_status()
            rows = json.loads(response.json()["choices"][0]["message"]["content"])["items"]
            if len(rows) != len(batch) or {str(row.get("id", "")) for row in rows} != expected:
                raise ValueError("معرفات دفعة المراجعة لا تطابق المرشحين")
            return [{
                "id": str(row["id"]),
                "final_decision": row["final_decision"],
                "reason": str(row["reason"])[:180],
                "confidence": max(0.0, min(1.0, float(row["confidence"]))),
            } for row in rows]
        except Exception as exc:
            error = str(exc)
            time.sleep(min(2 ** attempt, 12))
    return [{
        "id": str(item["id"]),
        "final_decision": "REVIEW",
        "reason": f"تعذر تأكيد الحذف: {error[:120]}",
        "confidence": 0.0,
    } for item in batch]


def load_progress() -> dict[str, dict]:
    for path in (PROGRESS_PATH, OUTPUT_PATH):
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return {str(row["id"]): row for row in data.get("reviews", [])}
    return {}


def save_progress(rows: dict[str, dict], total: int) -> None:
    payload = {"model": MODEL, "total_candidates": total, "reviewed_candidates": len(rows), "reviews": list(rows.values())}
    PROGRESS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    items = json.loads(ITEMS_PATH.read_text(encoding="utf-8"))
    first_pass = json.loads(CLASSIFICATIONS_PATH.read_text(encoding="utf-8"))["classifications"]
    remove_ids = {str(row["id"]) for row in first_pass if row["decision"] == "REMOVE"}
    candidates = [item for item in items if str(item["id"]) in remove_ids]
    existing = load_progress()
    pending = [item for item in candidates if str(item["id"]) not in existing]
    batches = [pending[i:i + BATCH_SIZE] for i in range(0, len(pending), BATCH_SIZE)]
    print(f"مرشحو الحذف: {len(candidates)} | المنجز سابقاً: {len(existing)} | المتبقي: {len(pending)}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(review_batch, batch): index for index, batch in enumerate(batches, 1)}
        for number, future in enumerate(concurrent.futures.as_completed(futures), 1):
            for row in future.result():
                existing[row["id"]] = row
            save_progress(existing, len(candidates))
            print(f"راجعت الدفعة {number}/{len(batches)} | قرارات محفوظة: {len(existing)}", flush=True)

    final = [existing[str(item["id"])] for item in candidates]
    OUTPUT_PATH.write_text(json.dumps({"model": MODEL, "total_candidates": len(candidates), "reviews": final}, ensure_ascii=False, indent=2), encoding="utf-8")
    if PROGRESS_PATH.exists():
        PROGRESS_PATH.unlink()
    print(f"اكتملت مراجعة {len(final)} مرشح حذف")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
