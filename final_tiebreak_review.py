#!/usr/bin/env python3
"""تحكيم أخير لحالات REVIEW المتبقية؛ لا يعدّل أي بيانات منشورة."""

from __future__ import annotations

import concurrent.futures
import json
import os
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "title_review_third_pass.json"
OUTPUT = ROOT / "title_review_third_pass_final.json"
MODEL = "gpt-5-mini"
BATCH_SIZE = 40
WORKERS = 8


def load() -> list[dict]:
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    return [row for row in data["decisions"] if row["decision"] == "REVIEW"]


def payload(batch: list[dict]) -> dict:
    records = []
    for row in batch:
        ctx = row.get("context", {})
        records.append({
            "id": row["id"],
            "title": ctx.get("title", ""),
            "author": ctx.get("author", ""),
            "publisher": ctx.get("publisher", ""),
            "source": ctx.get("source", ""),
            "category": ctx.get("category", ""),
            "material_type": ctx.get("material_type", ""),
            "file_type": ctx.get("file_type", ""),
            "pages_count": ctx.get("pages_count", ""),
            "link_telegram": ctx.get("link_telegram", ""),
            "link_direct": ctx.get("link_direct", ""),
            "link_drive": ctx.get("link_drive", ""),
            "previous_review_reason": row.get("reason", ""),
        })
    prompt = f"""أنت المحكّم النهائي لمكنز القضاء والأنظمة والمحاماة. هذه حالات بقيت REVIEW بعد فحص سابق للعنوان والبيانات والرابط حيث أمكن. احسمها إلى KEEP أو REMOVE ما لم يكن استحالة الحسم حقيقية حتى بعد كل الحقول والسبب السابق.

معيار ملزم: KEEP للأنظمة السعودية/القانونية، المحاكم والقضاء، القاضي بوصفه موضوعاً قضائياً، التحكيم، الإثبات، الجنايات، الأحوال الشخصية، المعاملات القانونية، والتراث القضائي الفعلي. REMOVE للقضاء والقدر، قضاء الصلاة والعبادات، القضاء على ظاهرة/مرض/شخص، القضاء التقسيم الجغرافي، المحكمة المجازية أو المجلات المحكمة، القاضي لقب لمؤلف في موضوع حديثي أو أدبي أو لغوي، والموضوعات التربوية والصحية والجغرافية والعقدية والأدبية والسياسية غير القانونية. لا تجعل كلمة واحدة سبباً للحكم.

أمثلة واجبة: المدخل إلى دراسة الأنظمة السعودية KEEP؛ أثر القرار الإداري على جودة القيادة REMOVE؛ معوقات القرار الإداري المدرسي REMOVE؛ قضاء الكاظمية الجغرافي REMOVE؛ تعقبات القاضي عياض الحديثية REMOVE؛ رسائل القاضي الفاضل الأسلوبية REMOVE؛ ظفر اللاضي بما يجب في القضاء على القاضي KEEP ما لم يكشف السياق خلاف ذلك.

لا تستخدم REVIEW إلا إذا كان العنوان غامضاً فعلاً أو دلّت الحقول على احتمالات متناقضة لا يرجّح أحدها. اذكر سبباً عربياً وجيزاً يستند إلى السياق الكامل.

السجلات:\n{json.dumps(records, ensure_ascii=False)}"""
    return {
        "model": MODEL,
        "messages": [{"role": "system", "content": "أنت محكّم قانوني دقيق. أخرج JSON مطابقاً للمخطط فقط."}, {"role": "user", "content": prompt}],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "final_tiebreak",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {"items": {"type": "array", "items": {"type": "object", "properties": {"id": {"type": "string"}, "decision": {"type": "string", "enum": ["KEEP", "REMOVE", "REVIEW"]}, "reason": {"type": "string"}, "confidence": {"type": "number"}}, "required": ["id", "decision", "reason", "confidence"], "additionalProperties": False}}},
                    "required": ["items"], "additionalProperties": False,
                },
            },
        },
        "max_completion_tokens": 7000,
    }


def run(batch: list[dict]) -> list[dict]:
    expected = {str(row["id"]) for row in batch}
    for attempt in range(4):
        try:
            res = requests.post(f"{os.environ['OPENAI_API_BASE'].rstrip('/')}/chat/completions", headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}", "Content-Type": "application/json"}, json=payload(batch), timeout=240)
            res.raise_for_status()
            rows = json.loads(res.json()["choices"][0]["message"]["content"])["items"]
            if len(rows) != len(batch) or {str(row["id"]) for row in rows} != expected:
                raise ValueError("مخرجات غير مطابقة")
            return rows
        except Exception:
            time.sleep(min(2 ** (attempt + 1), 10))
    return [{"id": row["id"], "decision": "REVIEW", "reason": "تعذر الحسم التقني بعد محاولات متعددة", "confidence": 0.0} for row in batch]


def main() -> int:
    review = load()
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    lookup = {str(row["id"]): row for row in source["decisions"]}
    batches = [review[i:i + BATCH_SIZE] for i in range(0, len(review), BATCH_SIZE)]
    verdicts = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = [executor.submit(run, batch) for batch in batches]
        for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
            verdicts.extend(future.result())
            print(f"التحكيم النهائي: {index}/{len(batches)}", flush=True)
    for row in verdicts:
        row["context"] = lookup[str(row["id"])]["context"]
        row["previous_reason"] = lookup[str(row["id"])].get("reason", "")
    output = {
        "total_input_review": len(review),
        "decisions": verdicts,
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"اكتمل التحكيم: {len(verdicts)} حالة", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
