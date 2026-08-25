import concurrent.futures as futures
import json
import os
import time
from pathlib import Path
from openai import OpenAI

ROOT = Path('/home/ubuntu/makanez-qadaa')
RECORDS = json.loads((ROOT / 'ibrazx40_source_audit_records.json').read_text(encoding='utf-8'))['records']
OUT = ROOT / 'ibrazx40_source_initial_classifications.json'
client = OpenAI()

SYSTEM = '''أنت مراجع عربي دقيق لمكنز القضاء والأنظمة والمحاماة. صنف سجلاً واحداً فقط إلى KEEP أو REMOVE أو REVIEW. 
KEEP: قانون دولي مباشر، معاهدات، منظمات دولية في إطار قانوني، قانون إنساني/جنائي دولي، تحكيم/قضاء دولي، حقوق إنسان قانونية، مسؤولية دولية، بحار وحدود وسيادة وحصانات، لجوء/جنسية/هجرة قانونية.
REMOVE: سياسة خارجية، علاقات دولية عامة، أمن أو استراتيجية، تاريخ سياسي/دبلوماسي، جغرافيا سياسية، اقتصاد دولي بحت، فكر سياسي أو حزبي أو أيديولوجي أو مذهبي، ما لم يدل العنوان والبيانات على معالجة قانونية دولية مباشرة.
REVIEW: غموض حقيقي لا يمكن حسمه بالعنوان والتصنيف والبيانات المتاحة. لا تجعل وجود ألفاظ إيران أو فلسطين أو إسرائيل أو إرهاب أو منظمات أو دول سبباً مستقلاً للحذف.
استخدم بيانات السجل فقط. اذكر سبباً عربياً محدداً مرتبطاً بالعنوان والتصنيف، ولا تقترح حذفاً بالتخمين.'''

SCHEMA = {
    'type': 'json_schema',
    'json_schema': {
        'name': 'international_law_classification',
        'strict': True,
        'schema': {
            'type': 'object',
            'properties': {
                'decision': {'type': 'string', 'enum': ['KEEP', 'REMOVE', 'REVIEW']},
                'reason': {'type': 'string'},
                'confidence': {'type': 'integer', 'minimum': 0, 'maximum': 100},
                'legal_basis': {'type': 'string'},
            },
            'required': ['decision', 'reason', 'confidence', 'legal_basis'],
            'additionalProperties': False,
        },
    },
}

def classify(record):
    payload = {k: record.get(k, '') for k in ['id','title','author','investigator','publisher','year','source','category','material_type','file_type','link_telegram','link_drive','link_direct','pages_count']}
    error = None
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model='gpt-5-mini',
                messages=[{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': json.dumps(payload, ensure_ascii=False)}],
                response_format=SCHEMA,
                max_completion_tokens=450,
            )
            data = json.loads(response.choices[0].message.content)
            return {'id': record['id'], 'title': record['title'], 'source': record['source'], 'category': record['category'], **data, 'error': ''}
        except Exception as exc:
            error = str(exc)
            time.sleep(1.5 * (attempt + 1))
    return {'id': record['id'], 'title': record['title'], 'source': record['source'], 'category': record['category'], 'decision': 'REVIEW', 'reason': 'تعذر استكمال التصنيف الآلي؛ يلزم تحكيم لاحق.', 'confidence': 0, 'legal_basis': '', 'error': error}

with futures.ThreadPoolExecutor(max_workers=8) as pool:
    rows = list(pool.map(classify, RECORDS))
rows.sort(key=lambda row: row['id'])
result = {'generated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'source': 'القانون الدولي العام', 'total': len(rows), 'classifications': rows}
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
counts = {label: sum(row['decision'] == label for row in rows) for label in ['KEEP','REMOVE','REVIEW']}
print(json.dumps({'total': len(rows), **counts, 'errors': sum(bool(row['error']) for row in rows)}, ensure_ascii=False))
