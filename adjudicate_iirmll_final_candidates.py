from datetime import datetime, timezone
import json
import time
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / 'iirmll_merged_audit_reviews.json'
OUTPUT = ROOT / 'iirmll_final_adjudications.json'
MODEL = 'gpt-5.5'
client = OpenAI()

SYSTEM = """أنت محكم نهائي مستقل لمكنز القضاء والأنظمة والمحاماة. افصل في حالة فحص محددة بقرار واحد: KEEP أو REMOVE أو REVIEW. كن متحفظاً في الحذف، ولا تحذف إلا إذا دل العنوان والتصنيف والبيانات على خروج واضح عن القانون أو القضاء أو الأنظمة أو المحاماة. أبقِ التنظيم القانوني أو المعالجة القانونية للسياسة أو الحقوق أو العلاقات الدولية. احذف السياسة العامة أو المذهبية أو الأيديولوجية أو التاريخ أو الإدارة أو الاقتصاد أو الدين العام إذا لم تكن المعالجة قانونية. REVIEW للغموض الحقيقي فقط. أعد JSON فقط."""
SCHEMA = {
    'type': 'json_schema',
    'json_schema': {
        'name': 'final_iirmll_adjudication',
        'strict': True,
        'schema': {
            'type': 'object',
            'properties': {
                'decision': {'type': 'string', 'enum': ['KEEP', 'REMOVE', 'REVIEW']},
                'reason': {'type': 'string'},
                'confidence': {'type': 'integer', 'minimum': 0, 'maximum': 100},
            },
            'required': ['decision', 'reason', 'confidence'],
            'additionalProperties': False,
        },
    },
}

def adjudicate(entry):
    payload = {
        'record': entry['record'],
        'initial': entry['initial'],
        'critical': entry['critical'],
        'provisional_decision': entry['provisional_decision'],
        'provisional_reason': entry['provisional_reason'],
    }
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)}],
                response_format=SCHEMA,
                max_completion_tokens=700,
                extra_body={'reasoning': {'effort': 'high'}},
            )
            return {'id': entry['id'], 'title': entry['title'], 'adjudication': json.loads(response.choices[0].message.content), 'error': None}
        except Exception as exc:
            if attempt == 2:
                return {'id': entry['id'], 'title': entry['title'], 'adjudication': None, 'error': str(exc)}
            time.sleep(2 * (attempt + 1))

def main():
    candidates = json.loads(INPUT.read_text(encoding='utf-8'))['adjudication_queue']
    results = [adjudicate(entry) for entry in candidates]
    output = {'generated_at': datetime.now(timezone.utc).isoformat(), 'model': MODEL, 'candidate_count': len(candidates), 'adjudications': results, 'error_count': sum(1 for row in results if row['error'])}
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'candidate_count': len(candidates), 'error_count': output['error_count'], 'output': str(OUTPUT)}, ensure_ascii=False, indent=2))
    if output['error_count']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
