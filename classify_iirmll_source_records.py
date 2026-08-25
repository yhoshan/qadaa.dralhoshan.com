from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time

from openai import OpenAI

ROOT = Path(__file__).resolve().parent
INPUT_PATH = ROOT / "iirmll_source_audit_records.json"
OUTPUT_PATH = ROOT / "iirmll_source_initial_classifications.json"
MODEL = "gpt-5-mini"
MAX_WORKERS = 8

SYSTEM_PROMPT = """أنت محكم موضوعي دقيق لمكنز القضاء والأنظمة والمحاماة. افحص سجلاً واحداً من مصدر المكتبة القانونية فقط، اعتماداً على العنوان والتصنيف والمصدر والرابط والبيانات الوصفية المتاحة.

أصدر حكماً واحداً فقط: KEEP أو REMOVE أو REVIEW.

KEEP: كل مادة قانونية أو قضائية أو نظامية مباشرة، مثل الأنظمة والقوانين واللوائح، القضاء والأحكام، المحاماة، المرافعات والإجراءات، الإثبات، التحكيم والوساطة، القانون المدني والتجاري والجنائي والإداري والدستوري والدولي والإنساني، حقوق الإنسان قانونياً، الجرائم الدولية والإرهاب قانونياً، الملكية الفكرية، قانون العمل، الشركات، الاستثمار والضرائب والزكاة قانونياً أو تنظيمياً، والدراسات المقارنة والفقه القضائي والمعاملات ذات الصلة المباشرة.

REMOVE: السياسة العامة أو الحزبية أو الأيديولوجية أو المذهبية أو الدعائية أو الحركية أو الثورية، التاريخ السياسي والمذكرات السياسية، العلاقات الدولية أو الدراسات الاستراتيجية بلا معالجة قانونية، والموضوعات الاقتصادية أو الإدارية أو المحاسبية أو التنموية أو الاجتماعية أو الإعلامية أو التربوية أو التاريخية أو الأدبية أو الدينية العامة الخارجة عن اختصاص المكنز.

لا تحذف بسبب كلمة منفردة. مثال: التنظيم القانوني للأحزاب KEEP، أما تاريخ الأحزاب بلا معالجة قانونية REMOVE. انتبه للمطابقات الكاذبة: الحكم بمعنى حكمة أو رأي، القضاء والقدر، النظام الاجتماعي أو الفكري، الحقوق الدينية أو الأخلاقية، العقود الزمنية، الملكية كنظام سياسي، العمل الإداري أو الاقتصادي، والمحكمة بمعنى الإحكام أو عنوان تراثي بعيد عن المحاكم.

لا تجعل نقص المؤلف أو الناشر أو السنة سبباً لـ REVIEW؛ وجود عنوان مناسب ورابط كافٍ. استعمل REVIEW فقط عند غموض حقيقي أو عنوان مبتور لا يكفي للحسم. السبب يجب أن يكون عربياً محدداً ومتصلاً بالمحتوى، وليس عبارة عامة مثل «سياسي» وحدها.

أعد JSON فقط يطابق المخطط المطلوب."""

SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "iirmll_classification",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "decision": {"type": "string", "enum": ["KEEP", "REMOVE", "REVIEW"]},
                "reason": {"type": "string"},
                "confidence": {"type": "integer", "minimum": 0, "maximum": 100},
                "signals": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["decision", "reason", "confidence", "signals"],
            "additionalProperties": False,
        },
    },
}

client = OpenAI()

def classify(record):
    compact = {
        "id": record["id"],
        "title": record.get("title", ""),
        "author": record.get("author", ""),
        "source": record.get("source", ""),
        "category": record.get("category", ""),
        "material_type": record.get("material_type", ""),
        "file_type": record.get("file_type", ""),
        "description": record.get("description", ""),
        "links": record.get("links", {}),
    }
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": json.dumps(compact, ensure_ascii=False)},
                ],
                response_format=SCHEMA,
                max_completion_tokens=350,
            )
            payload = json.loads(response.choices[0].message.content)
            return {"id": record["id"], "title": record.get("title", ""), **payload, "error": None}
        except Exception as exc:
            if attempt == 2:
                return {"id": record["id"], "title": record.get("title", ""), "decision": "REVIEW", "reason": "تعذر إتمام التصنيف الآلي بعد إعادة المحاولة؛ يلزم فحص بشري للبيانات المتاحة.", "confidence": 0, "signals": ["processing_error"], "error": str(exc)}
            time.sleep(1.5 * (attempt + 1))

def main():
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    records = source["records"]
    results = [None] * len(records)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(classify, record): index for index, record in enumerate(records)}
        for future in as_completed(futures):
            index = futures[future]
            results[index] = future.result()
    errors = [result for result in results if result["error"]]
    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "total_records": len(records),
        "classifications": results,
        "error_count": len(errors),
    }
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = {decision: sum(1 for result in results if result["decision"] == decision) for decision in ["KEEP", "REMOVE", "REVIEW"]}
    print(json.dumps({"total": len(records), "counts": counts, "errors": len(errors), "output": str(OUTPUT_PATH)}, ensure_ascii=False, indent=2))
    if len(results) != len(records):
        raise SystemExit(1)

if __name__ == "__main__":
    main()
