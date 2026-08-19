#!/usr/bin/env python3
"""جولة نهائية لحالات REVIEW فقط. لا تعدّل items.json أو النسخة المنشورة."""

from __future__ import annotations

import concurrent.futures
import json
import os
import re
import time
from html import unescape
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "title_review_second_pass_final.json"
PROGRESS = ROOT / "title_review_third_pass.progress.json"
OUTPUT = ROOT / "title_review_third_pass.json"
MODEL = "gpt-5-mini"
BATCH_SIZE = 25
MAX_WORKERS = 8
LINK_WORKERS = 12

EXAMPLES = """أمثلة ملزمة للمعيار:
- «المدخل إلى دراسة الأنظمة السعودية» = KEEP.
- «أثر القرار الإداري على جودة القيادة» = REMOVE.
- «أبرز معوقات صنع القرار الإداري المدرسي» = REMOVE.
- «تحليل جغرافي للوضع الأمني في قضاء الكاظمية» = REMOVE لأن القضاء هنا تقسيم جغرافي.
- «تعقبات القاضي عياض على صحيح الإمام» = REMOVE.
- «رسائل القاضي الفاضل دراسة أسلوبية» = REMOVE.
- «تقييم تدهور الأراضي في منطقة قضاء» = REMOVE.
- «ظفر اللاضي بما يجب في القضاء على القاضي» = KEEP ما لم يكشف السياق خلاف ذلك."""


def cases() -> list[dict]:
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    return [row for row in data["decisions"] if row["decision"] == "REVIEW"]


def load_progress() -> dict[str, dict]:
    for path in (PROGRESS, OUTPUT):
        if path.exists():
            return {str(row["id"]): row for row in json.loads(path.read_text(encoding="utf-8")).get("decisions", [])}
    return {}


def save(rows: dict[str, dict], total: int, final: bool = False) -> None:
    payload = {"model": MODEL, "total_cases": total, "decisions": list(rows.values())}
    (OUTPUT if final else PROGRESS).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def model_payload(batch: list[dict], final_pass: bool = False) -> dict:
    stage = "هذه مراجعة نهائية بعد إحضار بيانات الرابط حيث أمكن." if final_pass else "هذه مراجعة أولية، وأعد REVIEW فقط إذا كان فحص الرابط الأصلي ضرورياً للحسم."
    prompt = f"""أنت مراجع قانوني متخصص لمكنز القضاء والأنظمة والمحاماة. {stage}
استخدم العنوان كاملاً أولاً، ثم المؤلف والموضوع والتصنيف والمصدر والبيانات الوصفية. لا تعتبر كلمة منفردة مثل حكم أو قضاء أو محكمة أو حقوق أو نظام أو شهادة أو دعوى دليلاً كافياً.

KEEP عندما تثبت صلة حقيقية بالقضاء والمحاكم أو الأنظمة والقانون أو المحاماة أو التحكيم أو الإثبات أو الجنايات أو الأحوال الشخصية أو المعاملات القانونية، بما في ذلك التراث القضائي والفقهي المرتبط فعلاً بالقضاء.
REMOVE عندما يثبت أن «القضاء» بمعنى القضاء والقدر أو قضاء العبادة أو القضاء على ظاهرة، أو تقسيم جغرافي، أو محكمة التاريخ؛ أو «القاضي» مجرد لقب لمؤلف في موضوع حديثي/أدبي/لغوي؛ أو «محكمة/محكمة» تعني مجلة/بحوث محكّمة؛ أو كان الموضوع تربوياً أو صحياً أو جغرافياً أو عقدياً أو أدبياً أو سياسياً غير قانوني.
REVIEW فقط إن كانت البيانات والرابط المفحوص لا يكفيان حقيقة.

{EXAMPLES}

السجلات:
{json.dumps(batch, ensure_ascii=False)}"""
    return {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "أنت مراجع قانوني دقيق. اكتب JSON مطابقاً للمخطط فقط."},
            {"role": "user", "content": prompt},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "third_pass_decisions",
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
                                    "needs_link_check": {"type": "boolean"},
                                },
                                "required": ["id", "decision", "reason", "confidence", "needs_link_check"],
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
        "reasoning": {"effort": "low"},
    }


def decide(batch: list[dict], final_pass: bool = False) -> list[dict]:
    expected = {str(row["id"]) for row in batch}
    last = ""
    for attempt in range(4):
        try:
            response = requests.post(
                f"{os.environ['OPENAI_API_BASE'].rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}", "Content-Type": "application/json"},
                json=model_payload(batch, final_pass), timeout=300,
            )
            response.raise_for_status()
            output = json.loads(response.json()["choices"][0]["message"]["content"])["items"]
            if len(output) != len(batch) or {str(x.get("id")) for x in output} != expected:
                raise ValueError("مخرجات غير مطابقة للدفعة")
            return [{
                "id": str(row["id"]), "decision": row["decision"],
                "reason": str(row["reason"])[:300],
                "confidence": max(0.0, min(1.0, float(row["confidence"]))),
                "needs_link_check": bool(row["needs_link_check"]),
            } for row in output]
        except Exception as exc:
            last = str(exc)
            time.sleep(min(2 ** (attempt + 1), 14))
    return [{"id": row["id"], "decision": "REVIEW", "reason": f"تعذر الحسم التقني: {last[:150]}", "confidence": 0.0, "needs_link_check": True} for row in batch]


def source_url(context: dict) -> str:
    for field in ("link_direct", "link_drive", "link_telegram"):
        value = str(context.get(field, "")).strip()
        if value.startswith("http"):
            return value
    return ""


def page_metadata(context: dict) -> dict:
    url = source_url(context)
    if not url:
        return {"url": "", "status": "no_link", "title": "", "description": "", "snippet": ""}
    try:
        response = requests.get(url, timeout=18, headers={"User-Agent": "Mozilla/5.0 (compatible; MakanezReview/1.0)"}, allow_redirects=True)
        text = response.text[:150000] if "text" in response.headers.get("Content-Type", "") else ""
        soup = BeautifulSoup(text, "html.parser") if text else None
        title = soup.title.get_text(" ", strip=True) if soup and soup.title else ""
        meta = ""
        if soup:
            node = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
            meta = node.get("content", "") if node else ""
            body = soup.get_text(" ", strip=True)
        else:
            body = ""
        body = re.sub(r"\s+", " ", unescape(body))[:1200]
        return {"url": response.url, "status": str(response.status_code), "title": title[:300], "description": meta[:500], "snippet": body}
    except Exception as exc:
        return {"url": url, "status": f"error:{type(exc).__name__}", "title": "", "description": "", "snippet": ""}


def enrich(rows: list[dict], lookup: dict[str, dict]) -> list[dict]:
    needs = [row for row in rows if row["decision"] == "REVIEW" or row["needs_link_check"]]
    cache = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=LINK_WORKERS) as executor:
        futures = {executor.submit(page_metadata, lookup[row["id"]]["context"]): row["id"] for row in needs}
        for future in concurrent.futures.as_completed(futures):
            cache[futures[future]] = future.result()
    result = []
    for row in rows:
        ctx = dict(lookup[row["id"]]["context"])
        if row["id"] in cache:
            ctx["page_metadata"] = cache[row["id"]]
        result.append({**ctx, "first_pass": row})
    return result


def run_stage(rows: list[dict], final_pass: bool = False) -> list[dict]:
    batches = [rows[i:i + BATCH_SIZE] for i in range(0, len(rows), BATCH_SIZE)]
    all_rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(decide, batch, final_pass) for batch in batches]
        for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
            all_rows.extend(future.result())
            print(f"{'الحسم بعد الرابط' if final_pass else 'الحسم الأولي'}: {index}/{len(batches)}", flush=True)
    return all_rows


def main() -> int:
    input_cases = cases()
    lookup = {str(row["id"]): row for row in input_cases}
    saved = load_progress()
    if saved:
        print(f"استئناف نتيجة محفوظة: {len(saved)}", flush=True)
        final_rows = list(saved.values())
    else:
        print(f"بدء الجولة الثالثة: {len(input_cases)} حالة", flush=True)
        first_input = [dict(row["context"], previous_second_pass_reason=row["reason"], previous_second_pass_confidence=row["confidence"]) for row in input_cases]
        first_rows = run_stage(first_input, final_pass=False)
        print("بدء فحص روابط الحالات غير المحسومة", flush=True)
        enriched = enrich(first_rows, lookup)
        final_rows = run_stage(enriched, final_pass=True)
        mapped = {row["id"]: row for row in final_rows}
        for row in final_rows:
            row["context"] = lookup[row["id"]]["context"]
        save(mapped, len(input_cases))
    mapped = {row["id"]: row for row in final_rows}
    for row in final_rows:
        row.setdefault("context", lookup[row["id"]]["context"])
    save(mapped, len(input_cases), final=True)
    if PROGRESS.exists():
        PROGRESS.unlink()
    print(f"اكتملت الجولة الثالثة: {len(final_rows)} حالة", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
