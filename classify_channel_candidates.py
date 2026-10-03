#!/usr/bin/env python3
"""Semantic second-pass review of candidate legal titles, read-only.

Input is the deterministic candidate CSV produced by screen_qadaiyat_and_hadeeth_channels.py.
Output does not modify items.json.  The final integration script must consume only KEEP
results from this file and still apply duplicate safeguards.
"""
from __future__ import annotations

import concurrent.futures as futures
import csv
import json
import os
import time
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parent
INFILE = ROOT / 'qadaiyat_and_hadeeth_2026-10-03_screening' / 'keep_candidates.csv'
OUTDIR = ROOT / 'qadaiyat_and_hadeeth_2026-10-03_semantic_review'
OUTDIR.mkdir(exist_ok=True)
OUTFILE = OUTDIR / 'semantic_review.csv'
SUMMARY = OUTDIR / 'semantic_review_summary.json'
MODEL = 'gpt-5-mini'
WORKERS = 8

SYSTEM = '''أنت مدقق فهرس عربي متخصص في القضاء والأنظمة والمحاماة. مهمتك تصنيف عنوان واحد فقط.

اختر KEEP فقط إذا كان العنوان يدل بوضوح على مادة تصلح في مكنز القضاء والأنظمة والمحاماة: نظام أو قانون أو لائحة أو قرار؛ قضاء أو محكمة أو دعوى أو مرافعة أو تنفيذ أو إثبات؛ محاماة؛ تحكيم أو وساطة؛ قانون مدني أو تجاري أو إداري أو دستوري أو عمالي أو جنائي؛ أو دراسة فقهية يكون موضوعها المركزي القضاء أو القاضي أو الجنايات أو الإثبات أو التحكيم أو العقود والمعاملات القانونية.

اختر EXCLUDE إذا كان العنوان دينيًا عامًا أو لغويًا أو أدبيًا أو تربويًا أو طبيًا أو إعلاميًا أو تطويرًا ذاتيًا، أو إذا كان لا يكفي العنوان لإثبات الصلة القانونية/القضائية. لا تحتفظ بالمادة لمجرد وجود كلمات: حكم، فقه، عمل، أو حقوق. لا تضف معلومات ليست في العنوان.

أعد JSON فقط وفق المخطط المطلوب.'''

SCHEMA = {
    'type': 'json_schema',
    'json_schema': {
        'name': 'channel_title_scope_review',
        'strict': True,
        'schema': {
            'type': 'object',
            'properties': {
                'decision': {'type': 'string', 'enum': ['KEEP', 'EXCLUDE']},
                'confidence': {'type': 'number'},
                'reason': {'type': 'string'},
            },
            'required': ['decision', 'confidence', 'reason'],
            'additionalProperties': False,
        },
    },
}


def review(client: OpenAI, row: dict) -> dict:
    prompt = (
        'القناة: ' + row['channel_name'] + '\n'
        'العنوان بعد تنظيف اسم الملف: ' + row['title'] + '\n'
        'التصنيف الأولي: ' + row['category'] + '\n'
        'نوع المادة الأولي: ' + row['material_type']
    )
    last = None
    for attempt in range(4):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{'role':'system','content':SYSTEM},{'role':'user','content':prompt}],
                response_format=SCHEMA,
                max_completion_tokens=300,
            )
            payload = json.loads(response.choices[0].message.content)
            if payload['decision'] not in {'KEEP','EXCLUDE'}:
                raise ValueError('unexpected decision')
            payload['confidence'] = float(payload['confidence'])
            return payload
        except Exception as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
    return {'decision':'EXCLUDE','confidence':0.0,'reason':f'فشل التصنيف الآلي: {type(last).__name__}'}


def main() -> None:
    rows = list(csv.DictReader(INFILE.open(encoding='utf-8-sig')))
    client = OpenAI()
    outputs = [None] * len(rows)
    with futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        todo = {pool.submit(review, client, row): index for index, row in enumerate(rows)}
        for completed in futures.as_completed(todo):
            i = todo[completed]
            outputs[i] = completed.result()
            if (i + 1) % 50 == 0:
                print(f'completed {i+1}/{len(rows)}', flush=True)
    final = []
    for row, outcome in zip(rows, outputs):
        final.append({**row,
                      'semantic_decision': outcome['decision'],
                      'semantic_confidence': f"{outcome['confidence']:.3f}",
                      'semantic_reason': outcome['reason']})
    fields = list(final[0])
    with OUTFILE.open('w',encoding='utf-8-sig',newline='') as handle:
        writer = csv.DictWriter(handle,fieldnames=fields)
        writer.writeheader(); writer.writerows(final)
    summary = {
        'model': MODEL,
        'reviewed': len(final),
        'decision_counts': {d: sum(r['semantic_decision']==d for r in final) for d in ['KEEP','EXCLUDE']},
        'keep_high_confidence': sum(r['semantic_decision']=='KEEP' and float(r['semantic_confidence']) >= 0.85 for r in final),
        'keep_low_confidence': sum(r['semantic_decision']=='KEEP' and float(r['semantic_confidence']) < 0.85 for r in final),
        'per_source': {},
        'input_file': str(INFILE),
        'note': 'هذه مراجعة دلالية للعنوان والسياق الوصفي فقط؛ لا تغيّر قاعدة البيانات ولا تكفي لتجاوز فحص التكرار اللاحق.'
    }
    for source in sorted(set(r['channel_name'] for r in final)):
        selected = [r for r in final if r['channel_name']==source]
        summary['per_source'][source] = {
          'reviewed':len(selected),
          'keep':sum(r['semantic_decision']=='KEEP' for r in selected),
          'exclude':sum(r['semantic_decision']=='EXCLUDE' for r in selected),
          'keep_high_confidence':sum(r['semantic_decision']=='KEEP' and float(r['semantic_confidence'])>=0.85 for r in selected),
        }
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
