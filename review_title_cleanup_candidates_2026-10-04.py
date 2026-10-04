#!/usr/bin/env python3
"""Classify public title-cleanup candidates without changing project data.
Produces a reviewable decision dataset for a subsequent guarded integration.
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import os
import time
from collections import Counter
from pathlib import Path
from typing import Any

from openai import OpenAI

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "title_cleanup_2026-10-04_inventory.json"
OUTPUT = ROOT / "title_cleanup_2026-10-04_model_review.json"
PROGRESS = ROOT / ".title_cleanup_model_review_2026-10-04.jsonl"
MODEL = "gpt-5-mini"
BATCH_SIZE = 8
WORKERS = 8

SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "decision": {"type": "string", "enum": ["REWRITE", "KEEP", "INTERNAL"]},
                    "proposed_title": {"type": "string"},
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                    "rationale": {"type": "string"},
                },
                "required": ["id", "decision", "proposed_title", "confidence", "rationale"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["items"],
    "additionalProperties": False,
}

SYSTEM = """أنت محرر فهرس قانوني عربي شديد التحفظ. راجع عناوين سجلات مكنز القضاء والأنظمة والمحاماة.
المطلوب تحسين صياغة العنوان فقط، لا حذف سجل ولا تغيير أي حقل آخر ولا اختراع معلومات.

القرارات:
- REWRITE: عندما تسمح بيانات العنوان ذاته بصياغة عنوان عربي مهني واضح، بعد إزالة امتداد ملف أو رقم فهرسة أو كلمات تقنية أو وصف إرسال أو بيانات زائدة. اكتب العنوان النهائي فقط، بلا امتداد ولا أسماء قنوات ولا مديح ولا تعليمات تنزيل. لا تنقل بيانات غير مؤكدة إلى العنوان.
- KEEP: عندما يكون العنوان الحالي واضحاً ومهنياً في جوهره ولا يحتاج إلا إلى تعديل شكلي طفيف غير ضروري؛ أعد العنوان نفسه حرفياً.
- INTERNAL: عندما يكون العنوان مبتوراً أو غامضاً أو مجرد وصف ملف أو لا يمكن استخراج عنوان واضح منه بثقة. عندها اجعل proposed_title سلسلة فارغة.

قواعد إلزامية:
1) إذا كان العنوان يتضمن اسم مؤلف متصلًا بوضوح ويمكن فصل العنوان عنه، يجوز استخدام شرطة طويلة ثم الاسم في العنوان فقط إذا كانت هذه المعلومة موجودة صراحة في النص؛ لا تخمّن.
2) لا تحوّل ملخصاً أو قائمة محتويات أو عبارة ترويجية إلى عنوان موضوعي مخترع؛ استخدم INTERNAL إن لم يتضح العنوان الأصلي.
3) لا تختصر اسماً قانونياً صحيحاً ولا تغير المعنى أو البلد أو السنة أو الرقم إذا كان جزءاً أصيلاً من العنوان.
4) لا تضع كلمات مثل PDF أو Doc أو File أو نسخة أو رابط أو تحميل أو قناة أو بريد أو version أو copy في العنوان النهائي.
5) العنوان النهائي يجب أن يكون عربياً أو يحفظ المصطلح القانوني الأجنبي الضروري، مختصراً ومناسباً للواجهة.
6) لا تعتمد على اسم المصدر لتخمين العنوان.
7) اجعل الثقة high فقط حين تكون الصياغة ظاهرة من النص نفسه.
"""


def call_batch(batch: list[dict[str, Any]], attempt: int = 1) -> list[dict[str, Any]]:
    client = OpenAI()
    content = json.dumps([
        {k: row.get(k, "") for k in ["id", "title", "author", "category", "material_type", "source", "proposed_title", "reasons"]}
        for row in batch
    ], ensure_ascii=False)
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": "راجع هذه السجلات بالترتيب. أخرج JSON مطابقاً للمخطط فقط:\n" + content},
            ],
            max_completion_tokens=4500,
            extra_body={"reasoning": {"effort": "minimal"}},
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "title_cleanup_review", "strict": True, "schema": SCHEMA},
            },
        )
        payload = json.loads(response.choices[0].message.content)
        result = payload["items"]
        expected = {x["id"] for x in batch}
        received = {x["id"] for x in result}
        if expected != received or len(result) != len(batch):
            raise ValueError(f"ID mismatch: expected={len(expected)} received={len(received)}")
        return result
    except Exception:
        if attempt >= 3:
            raise
        time.sleep(2 * attempt)
        return call_batch(batch, attempt + 1)


def main() -> None:
    rows = json.loads(INPUT.read_text(encoding="utf-8"))
    batches = [rows[i:i + BATCH_SIZE] for i in range(0, len(rows), BATCH_SIZE)]
    results: dict[str, dict[str, Any]] = {}
    if PROGRESS.exists():
        for line in PROGRESS.read_text(encoding="utf-8").splitlines():
            if line.strip():
                for decision in json.loads(line):
                    results[decision["id"]] = decision
    pending = [(i, batch) for i, batch in enumerate(batches) if not all(x["id"] in results for x in batch)]
    print(json.dumps({"total_candidates": len(rows), "batches": len(batches), "completed": len(results), "pending_batches": len(pending)}, ensure_ascii=False))
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {executor.submit(call_batch, batch): index for index, batch in pending}
        for completed, future in enumerate(cf.as_completed(futures), 1):
            batch_index = futures[future]
            decisions = future.result()
            with PROGRESS.open("a", encoding="utf-8") as fp:
                fp.write(json.dumps(decisions, ensure_ascii=False) + "\n")
            for decision in decisions:
                results[decision["id"]] = decision
            print(json.dumps({"completed_batches": completed, "total_pending": len(pending), "batch": batch_index, "decisions": Counter(x["decision"] for x in decisions)}, ensure_ascii=False), flush=True)
    merged = []
    for row in rows:
        decision = results[row["id"]]
        merged.append({**row, **decision})
    assert len(merged) == len(rows)
    OUTPUT.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = Counter(x["decision"] for x in merged)
    confidence = Counter(x["confidence"] for x in merged)
    print(json.dumps({"completed": len(merged), "decisions": summary, "confidence": confidence, "output": str(OUTPUT)}, ensure_ascii=False, default=dict))

if __name__ == "__main__":
    main()
