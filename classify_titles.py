#!/usr/bin/env python3
"""تصنيف دلالي آمن لجميع عناوين المكنز إلى KEEP أو REMOVE أو REVIEW.

لا يغيّر هذا البرنامج items.json. يكتب سجل قرارات قابل للاستئناف فقط.
"""

from __future__ import annotations

import concurrent.futures
import json
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
ITEMS_PATH = ROOT / "items.json"
POLICY_PATH = ROOT / "title_scope_policy.json"
OUTPUT_PATH = ROOT / "title_classifications.json"
PROGRESS_PATH = ROOT / "title_classifications.progress.json"

MODEL = "gpt-5-mini"
BATCH_SIZE = 100
MAX_WORKERS = 8
MAX_RETRIES = 4


def request_payload(batch: list[dict], policy: dict) -> dict:
    records = [{"id": str(item["id"]), "title": str(item.get("title", "")).strip()} for item in batch]
    instruction = f"""أنت مراجع علمي شديد التحفظ لعناوين مكنز القضاء والأنظمة والمحاماة.

المعيار الحاكم: {policy['title_only_rule']}

KEEP: {policy['decisions']['KEEP']}
REMOVE: {policy['decisions']['REMOVE']}
REVIEW: {policy['decisions']['REVIEW']}

قاعدة أمان إلزامية: {policy['safety_rule']}

أعد قراراً لكل سجل بالمعرف نفسه. لا تعتمد على المصدر أو التصنيف. اجعل السبب عربياً موجزاً ودقيقاً (12 كلمة كحد أقصى). confidence رقم من 0 إلى 1. لا تسقط أي سجل.

السجلات:
{json.dumps(records, ensure_ascii=False)}"""

    schema = {
        "type": "json_schema",
        "json_schema": {
            "name": "title_scope_classification",
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
                                "confidence": {"type": "number"}
                            },
                            "required": ["id", "decision", "reason", "confidence"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["items"],
                "additionalProperties": False
            }
        }
    }
    return {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "أنت مصنف دلالي حذر. أخرج JSON مطابقاً للمخطط فقط."},
            {"role": "user", "content": instruction}
        ],
        "response_format": schema,
        "max_completion_tokens": 6000
    }


def classify_batch(batch: list[dict], policy: dict) -> list[dict]:
    base = os.environ["OPENAI_API_BASE"].rstrip("/")
    api_key = os.environ["OPENAI_API_KEY"]
    url = f"{base}/chat/completions"
    expected_ids = {str(item["id"]) for item in batch}
    last_error = ""

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=request_payload(batch, policy),
                timeout=180,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            results = parsed["items"]
            found_ids = {str(row.get("id", "")) for row in results}
            if found_ids != expected_ids or len(results) != len(batch):
                raise ValueError("المعرفات المعادة لا تطابق الدفعة")
            normalized = []
            for row in results:
                decision = row.get("decision")
                if decision not in {"KEEP", "REMOVE", "REVIEW"}:
                    raise ValueError("قرار غير صالح")
                normalized.append({
                    "id": str(row["id"]),
                    "decision": decision,
                    "reason": str(row.get("reason", ""))[:180],
                    "confidence": max(0.0, min(1.0, float(row.get("confidence", 0)))),
                })
            return normalized
        except Exception as exc:  # سجلات الأعطال توضع REVIEW ولا تُحذف
            last_error = str(exc)
            time.sleep(min(2 ** attempt, 12))

    return [
        {
            "id": str(item["id"]),
            "decision": "REVIEW",
            "reason": f"تعذر التصنيف الآلي: {last_error[:120]}",
            "confidence": 0.0,
        }
        for item in batch
    ]


def load_existing() -> dict[str, dict]:
    for path in (PROGRESS_PATH, OUTPUT_PATH):
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return {str(row["id"]): row for row in data.get("classifications", [])}
    return {}


def checkpoint(existing: dict[str, dict], total: int) -> None:
    rows = [existing[key] for key in sorted(existing)]
    payload = {"model": MODEL, "total_items": total, "classified_items": len(rows), "classifications": rows}
    PROGRESS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    items = json.loads(ITEMS_PATH.read_text(encoding="utf-8"))
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    existing = load_existing()
    pending = [item for item in items if str(item["id"]) not in existing]
    batches = [pending[i:i + BATCH_SIZE] for i in range(0, len(pending), BATCH_SIZE)]
    print(f"إجمالي العناوين: {len(items)} | المنجَز سابقاً: {len(existing)} | المتبقي: {len(pending)}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(classify_batch, batch, policy): index for index, batch in enumerate(batches, 1)}
        for completed, future in enumerate(concurrent.futures.as_completed(futures), 1):
            batch_index = futures[future]
            for row in future.result():
                existing[row["id"]] = row
            checkpoint(existing, len(items))
            print(f"تمت الدفعة {completed}/{len(batches)} (رقم {batch_index}) | قرارات محفوظة: {len(existing)}", flush=True)

    final_rows = [existing[str(item["id"])] for item in items]
    payload = {"model": MODEL, "total_items": len(items), "classified_items": len(final_rows), "classifications": final_rows}
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if PROGRESS_PATH.exists():
        PROGRESS_PATH.unlink()
    print(f"اكتمل التصنيف: {len(final_rows)} عنواناً")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
