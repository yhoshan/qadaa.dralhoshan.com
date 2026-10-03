#!/usr/bin/env python3
"""Conservative LLM-assisted screening of the public export of مكتبة القاضي صلاح سيف.
Read-only: produces auditable raw/screening data and does not modify the catalogue.
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import json
import re
import time
import unicodedata
from collections import Counter
from pathlib import Path

from openai import OpenAI

ROOT = Path('/home/ubuntu/makanez-qadaa')
EXPORT = Path('/home/ubuntu/upload/pasted_file_xuKUhg_result.json')
RAW_OUT = ROOT / 'qadi_salah_2026-10-03_raw_pdf_inventory.json'
SCREENED_OUT = ROOT / 'qadi_salah_2026-10-03_llm_screening.json'
SUMMARY_OUT = ROOT / 'qadi_salah_2026-10-03_llm_screening_summary.json'
CHECKPOINT_DIR = ROOT / '.qadi_salah_llm_checkpoints'
MODEL = 'gpt-5-mini'
BATCH_SIZE = 20
WORKERS = 6

CONTROL = re.compile(r'[\u200e\u200f\u202a-\u202e\u2066-\u2069]')
# قرار نطاق صريح: لا تدخل مواد الأحزاب والتنظيمات والميليشيات السياسية
# في هذا المكنز ولو كان لها توصيف قانوني أو قضائي في العنوان.
POLITICAL_PATTERN = re.compile(
    r'الحوثي|الحوثيين|انصار الله|أنصار الله|حزب الله|حزب البعث|'
    r'حزب المؤتمر|المؤتمر الشعبي|الأحزاب|حزب سياسي|التنظيم السياسي|'
    r'المليشيا|الميليشيا|جماعة مسلحة',
    re.IGNORECASE,
)


def clean(value: str) -> str:
    value = unicodedata.normalize('NFKC', value or '')
    value = CONTROL.sub('', value)
    value = re.sub(r'\.(?:pdf|docx?|pptx?|zip)$', '', value, flags=re.I)
    value = value.replace('_', ' ')
    value = re.sub(r'\s+', ' ', value).strip(' .-_–—')
    return value


def text_value(message: dict) -> str:
    text = message.get('text', '')
    if isinstance(text, str):
        return clean(text)
    if isinstance(text, list):
        pieces = []
        for entry in text:
            if isinstance(entry, str): pieces.append(entry)
            elif isinstance(entry, dict): pieces.append(str(entry.get('text', '')))
        return clean(' '.join(pieces))
    return ''


def build_raw() -> list[dict]:
    data = json.loads(EXPORT.read_text(encoding='utf8'))
    messages = data.get('messages', [])
    raw = []
    last_substantive = ''
    last_substantive_id = -9999
    for message in messages:
        own_text = text_value(message)
        if message.get('type') == 'message' and own_text and not message.get('file_name'):
            last_substantive = own_text
            last_substantive_id = int(message.get('id', -9999))
        if message.get('type') != 'message' or message.get('mime_type') != 'application/pdf' or not message.get('file_name'):
            continue
        post_id = int(message['id'])
        context = own_text
        if not context and post_id - last_substantive_id <= 2:
            context = last_substantive
        raw.append({
            'post_id': post_id,
            'id': f'qadi_salah_{post_id}',
            'title': clean(str(message['file_name'])),
            'context': context[:700],
            'date': message.get('date', ''),
            'file_name': message.get('file_name', ''),
            'file_size_bytes': message.get('file_size'),
            'mime_type': message.get('mime_type'),
            'telegram_url': f'https://t.me/estsharesalah/{post_id}',
        })
    return raw


SYSTEM = '''أنت مُصنّف محتوى لمكنز القضاء والأنظمة والمحاماة.
صنّف كل ملف بناءً على العنوان والسياق المرفق فقط، ولا تخمّن محتوى غير مذكور.
KEEP فقط إذا كان الملف مادة قانونية أو قضائية واضحة: نظام/قانون/لائحة/قرار أو حكم وسابقة قضائية، أو بحث/رسالة/كتاب قانوني، أو مجلة قانونية، أو دليل مهني قانوني/قضائي/للمحاماة، أو اتفاقية/قواعد دولية قانونية. تقبل المواد السعودية والعربية والمقارنة، ومنها القوانين اليمنية.
REMOVE إذا كان أدباً أو رواية أو سيرة أو تاريخاً عاماً أو ديناً/فقهاً عاماً بلا اتصال قضائي/قانوني صريح، أو طباً/إدارة/اقتصاداً عاماً، أو تدريباً وإعلاناً أو مادة لا تثبت صلتها القانونية من العنوان والسياق.
REMOVE حتماً أي مادة تتناول الحوثيين أو أنصار الله أو حزب الله أو حزباً أو تنظيماً أو ميليشيا سياسية، ولو صيغت كوثيقة قانونية أو حكم أو قانون.
إذا كان العنوان غامضاً ولا يثبت اتصاله بالقانون والقضاء، اختر REMOVE احتياطاً.
اختر نوع المادة من القائمة حصراً: نظام، لائحة، قرار، أحكام، بحث، كتاب، شرح، دليل إجرائي، رسالة علمية، مجلة، اتفاقية دولية، قواعد دولية، قانون نموذجي، مادة قانونية، ملخص، مقال.
اختر التصنيف من القائمة حصراً: القضاء والأحكام والإجراءات، الأنظمة والقانون العام، القانون التجاري والمالي، القانون المدني والعقاري، القانون الجنائي، المحاماة والصياغة القانونية، القانون الدولي والمقارن، القانون الإداري والدستوري، الأحوال الشخصية والتركات، الدراسات القانونية، الملكية الفكرية.
'''

SCHEMA = {
    'type': 'json_schema',
    'json_schema': {
        'name': 'legal_batch_classification',
        'strict': True,
        'schema': {
            'type': 'object',
            'properties': {
                'rows': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'string'},
                            'decision': {'type': 'string', 'enum': ['KEEP', 'REMOVE']},
                            'material_type': {'type': 'string', 'enum': ['نظام','لائحة','قرار','أحكام','بحث','كتاب','شرح','دليل إجرائي','رسالة علمية','مجلة','اتفاقية دولية','قواعد دولية','قانون نموذجي','مادة قانونية','ملخص','مقال']},
                            'category': {'type': 'string', 'enum': ['القضاء والأحكام والإجراءات','الأنظمة والقانون العام','القانون التجاري والمالي','القانون المدني والعقاري','القانون الجنائي','المحاماة والصياغة القانونية','القانون الدولي والمقارن','القانون الإداري والدستوري','الأحوال الشخصية والتركات','الدراسات القانونية','الملكية الفكرية']},
                        },
                        'required': ['id','decision','material_type','category'],
                        'additionalProperties': False,
                    },
                },
            },
            'required': ['rows'],
            'additionalProperties': False,
        },
    },
}


def classify_batch(index: int, batch: list[dict]) -> list[dict]:
    CHECKPOINT_DIR.mkdir(exist_ok=True)
    checkpoint = CHECKPOINT_DIR / f'{index:04d}.json'
    expected = [x['id'] for x in batch]
    if checkpoint.exists():
        rows = json.loads(checkpoint.read_text(encoding='utf8'))
        if [x['id'] for x in rows] == expected:
            return rows
    payload = [{'id': x['id'], 'title': x['title'], 'context': x['context']} for x in batch]
    prompt = 'أعد صفاً واحداً بالترتيب نفسه لكل عنصر من العناصر التالية، ولا تحذف أي عنصر:\n' + json.dumps(payload, ensure_ascii=False)
    error = None
    for attempt in range(4):
        try:
            client = OpenAI()
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{'role':'system','content':SYSTEM},{'role':'user','content':prompt}],
                response_format=SCHEMA,
                max_completion_tokens=5000,
            )
            parsed = json.loads(response.choices[0].message.content)
            rows = parsed['rows']
            if [x['id'] for x in rows] != expected:
                raise ValueError(f'row IDs do not match batch {index}')
            checkpoint.write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n',encoding='utf8')
            return rows
        except Exception as exc:
            error = exc
            time.sleep(2 ** attempt)
    raise RuntimeError(f'batch {index} failed after retries: {error}')


def main() -> None:
    raw = build_raw()
    if len(raw) != 5184:
        raise AssertionError(f'expected 5184 PDF records, got {len(raw)}')
    ids = [x['id'] for x in raw]
    if len(ids) != len(set(ids)):
        raise AssertionError('duplicate source post IDs')
    RAW_OUT.write_text(json.dumps(raw, ensure_ascii=False, indent=2)+'\n',encoding='utf8')
    preexcluded = []
    to_classify = []
    for record in raw:
        combined = f"{record['title']} {record['context']}"
        if POLITICAL_PATTERN.search(combined):
            preexcluded.append({
                **record,
                'decision': 'REMOVE',
                'material_type': 'مادة قانونية',
                'category': 'الدراسات القانونية',
                'exclusion_reason': 'استبعاد سياسي صريح: يتناول حزباً أو تنظيماً أو جماعة/ميليشيا سياسية خارج نطاق المكنز.',
            })
        else:
            to_classify.append(record)
    batches = [to_classify[i:i+BATCH_SIZE] for i in range(0,len(to_classify),BATCH_SIZE)]
    all_rows: list[dict|None] = [None] * len(batches)
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {executor.submit(classify_batch, i, batch):i for i,batch in enumerate(batches)}
        for future in cf.as_completed(futures):
            index = futures[future]
            all_rows[index] = future.result()
            print(f'completed {index+1}/{len(batches)}', flush=True)
    decisions = {row['id']:row for group in all_rows for row in group}
    decisions.update({row['id']: row for row in preexcluded})
    if set(decisions) != set(ids):
        raise AssertionError('incomplete classification results')
    screened = [{**record, **decisions[record['id']]} for record in raw]
    SCREENED_OUT.write_text(json.dumps(screened, ensure_ascii=False, indent=2)+'\n',encoding='utf8')
    summary = {
        'model': MODEL,
        'source_channel': 'مكتبة القاضي صلاح سيف ⚖',
        'source_channel_id': 1109975427,
        'raw_pdf_records': len(raw),
        'preexcluded_political_records': len(preexcluded),
        'decisions': dict(Counter(x['decision'] for x in screened)),
        'kept_by_material_type': dict(Counter(x['material_type'] for x in screened if x['decision']=='KEEP')),
        'kept_by_category': dict(Counter(x['category'] for x in screened if x['decision']=='KEEP')),
        'raw_ids_sha256': hashlib.sha256('\n'.join(ids).encode()).hexdigest(),
        'screened_ids_sha256': hashlib.sha256('\n'.join(x['id'] for x in screened).encode()).hexdigest(),
        'batch_count': len(batches),
        'complete': True,
    }
    SUMMARY_OUT.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
