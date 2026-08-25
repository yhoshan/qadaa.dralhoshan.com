from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import os
import time
import traceback
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / 'iirmll_duplicate_candidates.json'
OUTPUT = ROOT / 'iirmll_duplicate_adjudications.json'
MODEL = 'gpt-5-mini'
MAX_WORKERS = 6
client = OpenAI()

SYSTEM = """أنت محكم تكرارات دقيق لمكنز قانوني. قيّم مجموعة سجلات متشابهة العنوان. لا تعدها تكراراً حقيقياً إلا إذا كانت الوثيقة نفسها فعلاً: عنوان واحد بعد الفروق الشكلية أو نسخة مكررة لها مع رابط/بيانات متطابقة أو دليل قوي. الأجزاء والمجلدات والطبعات المختلفة والموضوعات المتقاربة ليست تكراراً لمجرد التشابه. عند ثبوت التكرار اقترح نسخة مرجعية واحدة واذكر المعرفات الزائدة فقط. لا تطلب أو تنفذ حذفاً. أعد JSON فقط."""
SCHEMA = {
    'type': 'json_schema',
    'json_schema': {
        'name': 'iirmll_duplicate_adjudication',
        'strict': True,
        'schema': {
            'type': 'object',
            'properties': {
                'is_confirmed_duplicate': {'type': 'boolean'},
                'recommended_keep_id': {'type': ['string', 'null']},
                'redundant_ids': {'type': 'array', 'items': {'type': 'string'}},
                'reason': {'type': 'string'},
                'confidence': {'type': 'integer', 'minimum': 0, 'maximum': 100},
            },
            'required': ['is_confirmed_duplicate', 'recommended_keep_id', 'redundant_ids', 'reason', 'confidence'],
            'additionalProperties': False,
        },
    },
}

def judge(group):
    payload = {
        'group_id': group['group_id'],
        'candidate_reasons': group['candidate_reasons'],
        'records': [{key: record.get(key, '') for key in ['id', 'title', 'author', 'category', 'material_type', 'file_type', 'description', 'links', 'normalized_title']} for record in group['records']],
    }
    ids = {record['id'] for record in group['records']}
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)}],
                response_format=SCHEMA,
                max_completion_tokens=900,
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError('لم يُنتج النموذج محتوى قابلاً للقراءة')
            verdict = json.loads(content)
            if verdict['recommended_keep_id'] is not None and verdict['recommended_keep_id'] not in ids:
                raise ValueError('recommended id outside candidate group')
            if not set(verdict['redundant_ids']).issubset(ids):
                raise ValueError('redundant ids outside candidate group')
            return {'group_id': group['group_id'], 'records': group['records'], 'verdict': verdict, 'error': None}
        except Exception as exc:
            if attempt == 2:
                return {'group_id': group['group_id'], 'records': group['records'], 'verdict': None, 'error': f"{exc}\n{traceback.format_exc()}"}
            time.sleep(2 * (attempt + 1))

def main():
    groups = json.loads(INPUT.read_text(encoding='utf-8'))['groups']
    limit = int(os.environ.get('LIMIT', '0'))
    if limit:
        groups = groups[:limit]
    results = [None] * len(groups)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(judge, group): index for index, group in enumerate(groups)}
        for future in as_completed(futures):
            results[futures[future]] = future.result()
    output = {'generated_at': datetime.now(timezone.utc).isoformat(), 'model': MODEL, 'group_count': len(groups), 'adjudications': results, 'error_count': sum(1 for row in results if row['error'])}
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    confirmed = [row for row in results if row['verdict'] and row['verdict']['is_confirmed_duplicate']]
    redundant = sum(len(row['verdict']['redundant_ids']) for row in confirmed)
    print(json.dumps({'groups': len(groups), 'confirmed_groups': len(confirmed), 'redundant_ids': redundant, 'errors': output['error_count']}, ensure_ascii=False, indent=2))
    if output['error_count']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
