#!/usr/bin/env python3
"""فحص عينة عشوائية من 200 سجل بعد الإغلاق؛ لا يغير البيانات."""

from __future__ import annotations

import concurrent.futures
import json
import os
import random
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "items.json"
OUTPUT = ROOT / "final_closure_random_200_audit.json"
MODEL = "gpt-5-mini"
SEED = 20260819
BATCH_SIZE = 25
WORKERS = 8


def classify(batch: list[dict]) -> list[dict]:
    records = [{
        "id": str(item["id"]), "title": item.get("title", ""), "author": item.get("author", ""),
        "source": item.get("source", ""), "category": item.get("category", ""),
        "material_type": item.get("material_type", ""), "file_type": item.get("file_type", ""),
    } for item in batch]
    prompt = f"""أنت مدقق جودة مستقل لمكنز القضاء والأنظمة والمحاماة. افحص العينة التالية وحدد فقط السجلات الواضحة الخروج عن النطاق. النطاق يشمل القضاء والمحاكم والأنظمة والقانون والمحاماة والتحكيم والإثبات والجنايات والأحوال الشخصية والمعاملات القانونية والتراث القضائي المتصل مباشرة.
لا تحكم من كلمة مفردة. يعد واضح الخروج: القضاء والقدر، العبادات، القضاء على ظاهرة، قضاء جغرافي، أدب/لغة/حديث لا علاقة له بالقضاء، سياسة عامة أو إدارة أو صحة أو تعليم لا تعالج القانون، والمجلات المحكمة غير القانونية.
أخرج IN_SCOPE أو CLEAR_OUT_OF_SCOPE أو UNCERTAIN. لا تقترح حذفاً عند الشك.
السجلات:\n{json.dumps(records, ensure_ascii=False)}"""
    schema = {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {"id": {"type": "string"}, "verdict": {"type": "string", "enum": ["IN_SCOPE", "CLEAR_OUT_OF_SCOPE", "UNCERTAIN"]}, "reason": {"type": "string"}}, "required": ["id", "verdict", "reason"], "additionalProperties": False}}}, "required": ["items"], "additionalProperties": False}
    expected = {str(item["id"]) for item in batch}
    for attempt in range(4):
        try:
            response = requests.post(
                f"{os.environ['OPENAI_API_BASE'].rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}", "Content-Type": "application/json"},
                json={"model": MODEL, "messages": [{"role": "system", "content": "أنت مدقق دلالي دقيق. أخرج JSON فقط."}, {"role": "user", "content": prompt}], "response_format": {"type": "json_schema", "json_schema": {"name": "sample_audit", "strict": True, "schema": schema}}, "max_completion_tokens": 5000},
                timeout=240,
            )
            response.raise_for_status()
            rows = json.loads(response.json()["choices"][0]["message"]["content"])["items"]
            if len(rows) != len(batch) or {str(row["id"]) for row in rows} != expected:
                raise ValueError("نتيجة عينة غير مطابقة")
            return rows
        except Exception:
            time.sleep(min(2 ** (attempt + 1), 10))
    return [{"id": str(item["id"]), "verdict": "UNCERTAIN", "reason": "تعذر الفحص التقني"} for item in batch]


def main() -> int:
    items = json.loads(INPUT.read_text(encoding="utf-8"))
    rng = random.Random(SEED)
    sample = rng.sample(items, 200)
    lookup = {str(item["id"]): item for item in sample}
    batches = [sample[index:index + BATCH_SIZE] for index in range(0, len(sample), BATCH_SIZE)]
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = [executor.submit(classify, batch) for batch in batches]
        for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
            results.extend(future.result())
            print(f"فحص العينة: {index}/{len(batches)}", flush=True)
    for row in results:
        row["context"] = lookup[row["id"]]
    counts = {"IN_SCOPE": 0, "CLEAR_OUT_OF_SCOPE": 0, "UNCERTAIN": 0}
    for row in results:
        counts[row["verdict"]] += 1
    payload = {"seed": SEED, "sample_size": len(sample), "counts": counts, "decisions": results}
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"sample_size": len(sample), "counts": counts}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
