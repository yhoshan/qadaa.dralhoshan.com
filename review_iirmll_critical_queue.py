from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import time
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parent
QUEUE_PATH = ROOT / 'iirmll_critical_review_queue.json'
OUTPUT_PATH = ROOT / 'iirmll_critical_reviews.json'
MODEL = 'gpt-5'
MAX_WORKERS = 6
client = OpenAI()

SYSTEM = """أنت مراجع نقدي مستقل لمكنز القضاء والأنظمة والمحاماة. قيّم السجل وحده اعتماداً على العنوان والتصنيف والمصدر والرابط والبيانات المتاحة، ولا تتبع قرار المراجع الأول تلقائياً.

المواد القانونية والقضائية والنظامية المباشرة تبقى، بما فيها تنظيم الأحزاب أو حقوق الإنسان أو إيران أو الإرهاب إن كانت المعالجة قانونية. يُرشح للحذف فقط السياسي أو الحزبي أو الأيديولوجي أو المذهبي أو الدعائي أو الحركي أو التاريخ السياسي أو الاستراتيجي أو الاقتصادي/الإداري/الديني العام الذي لا يحمل معالجة قانونية مباشرة.

لا تجعل ظهور كلمة حساسة وحدها أساساً للحذف. انتبه للمطابقات اللفظية الكاذبة. REVIEW خاص بغموض حقيقي لا يمكن حسمه من البيانات المتاحة، لا لنقص المؤلف أو السنة. أعد قراراً واحداً فقط وأسباباً عربية محددة."""

SCHEMA = {
    'type': 'json_schema',
    'json_schema': {
        'name': 'critical_iirmll_review',
        'strict': True,
        'schema': {
            'type': 'object',
            'properties': {
                'decision': {'type': 'string', 'enum': ['KEEP', 'REMOVE', 'REVIEW']},
                'reason': {'type': 'string'},
                'confidence': {'type': 'integer', 'minimum': 0, 'maximum': 100},
                'policy_basis': {'type': 'string'},
            },
            'required': ['decision', 'reason', 'confidence', 'policy_basis'],
            'additionalProperties': False,
        },
    },
}

def review(entry):
    record = entry['record']
    payload = {
        'record': {key: record.get(key, '') for key in ['id', 'title', 'author', 'source', 'category', 'material_type', 'file_type', 'description', 'links']},
        'initial_decision': entry['initial']['decision'],
        'initial_reason': entry['initial']['reason'],
        'queue_triggers': entry['triggers'],
        'matched_terms': entry['matched_terms'],
    }
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)}],
                response_format=SCHEMA,
                max_completion_tokens=600,
                extra_body={'reasoning': {'effort': 'high'}},
            )
            verdict = json.loads(response.choices[0].message.content)
            return {'id': record['id'], 'title': record.get('title', ''), 'initial': entry['initial'], 'triggers': entry['triggers'], 'matched_terms': entry['matched_terms'], 'critical': verdict, 'error': None}
        except Exception as exc:
            if attempt == 2:
                return {'id': record['id'], 'title': record.get('title', ''), 'initial': entry['initial'], 'triggers': entry['triggers'], 'matched_terms': entry['matched_terms'], 'critical': None, 'error': str(exc)}
            time.sleep(2 * (attempt + 1))

def main():
    queue = json.loads(QUEUE_PATH.read_text(encoding='utf-8'))['queue']
    results = [None] * len(queue)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(review, entry): index for index, entry in enumerate(queue)}
        for future in as_completed(futures):
            results[futures[future]] = future.result()
    output = {'generated_at': datetime.now(timezone.utc).isoformat(), 'model': MODEL, 'queue_count': len(queue), 'reviews': results, 'error_count': sum(1 for result in results if result['error'])}
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    summary = {'KEEP': 0, 'REMOVE': 0, 'REVIEW': 0, 'ERROR': output['error_count']}
    for result in results:
        if result['critical']:
            summary[result['critical']['decision']] += 1
    print(json.dumps({'queue_count': len(queue), 'summary': summary, 'output': str(OUTPUT_PATH)}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
