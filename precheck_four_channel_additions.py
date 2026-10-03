#!/usr/bin/env python3
"""Apply confirmed title-level deduplication to four screened channel manifests.

This is a precheck only.  It writes a final addition manifest and a transparent audit;
it does not change the catalogue.  Duplicate decisions require an exact normalized
match after removal of purely technical/source-noise tokens.  It intentionally retains
different issues, volumes, parts, editions, and substantive variants.
"""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INFILE = ROOT / 'qadaiyat_and_hadeeth_2026-10-03_screening' / 'keep_manifest.json'
CATALOGUE = ROOT / 'items.json'
OUT = ROOT / 'qadaiyat_and_hadeeth_2026-10-03_precheck'
OUT.mkdir(exist_ok=True)

NOISE_TOKENS = {
    'pdf','doc','docx','secured','archivetemp','emailing','noor','book','موقع','النقض',
    'ktabaknachr','مكتبة','عبدالله','نسخة','نسخه',
}


def norm(value: str) -> str:
    value = unicodedata.normalize('NFKD', value or '')
    value = ''.join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower().translate(str.maketrans('٠١٢٣٤٥٦٧٨٩','0123456789'))
    value = value.replace('أ','ا').replace('إ','ا').replace('آ','ا').replace('ٱ','ا').replace('ى','ي').replace('ة','ه')
    return re.sub(r'[^\w\u0600-\u06ff]+',' ',value).strip()


def exact_key(title: str) -> str:
    return ''.join(norm(title).split())


def confirmed_key(title: str) -> str:
    """Remove only technical/source marks, retaining all content and numbering."""
    tokens=[token for token in norm(title).split() if token not in NOISE_TOKENS]
    return ''.join(tokens)


def main() -> None:
    current=json.loads(CATALOGUE.read_text(encoding='utf-8'))
    proposed=json.loads(INFILE.read_text(encoding='utf-8'))
    current_exact=defaultdict(list); current_confirmed=defaultdict(list)
    for item in current:
        title=str(item.get('title') or '')
        current_exact[exact_key(title)].append(item)
        current_confirmed[confirmed_key(title)].append(item)

    audit=[]; final=[]; kept_confirmed=defaultdict(list); ids=set()
    for item in proposed:
        row={
            'candidate_id': item['id'], 'title': item['title'], 'source': item['source'],
            'decision': '', 'reason': '', 'matched_ids': '', 'matched_titles': '',
            'official_url': item['link_telegram'],
        }
        if item['id'] in ids:
            raise SystemExit(f'duplicate candidate id {item["id"]}')
        ids.add(item['id'])
        key=exact_key(str(item['title']))
        exact=current_exact.get(key,[])
        if exact:
            row.update(decision='EXCLUDE_EXISTING_EXACT',reason='عنوان مطابق تماماً بعد التطبيع في المكنز الحالي.',
                       matched_ids=' | '.join(str(x.get('id')) for x in exact),
                       matched_titles=' | '.join(str(x.get('title')) for x in exact))
            audit.append(row); continue
        key2=confirmed_key(str(item['title']))
        confirmed=current_confirmed.get(key2,[])
        if confirmed:
            row.update(decision='EXCLUDE_EXISTING_CONFIRMED',
                       reason='عنوان مطابق بعد إزالة العلامات التقنية ومعلومات المصدر فقط، وهو نسخة زائدة مؤكدة.',
                       matched_ids=' | '.join(str(x.get('id')) for x in confirmed[:10]),
                       matched_titles=' | '.join(str(x.get('title')) for x in confirmed[:10]))
            audit.append(row); continue
        dupe=kept_confirmed.get(key2,[])
        if dupe:
            row.update(decision='EXCLUDE_BATCH_CONFIRMED',
                       reason='عنوان مطابق بعد إزالة العلامات التقنية ومعلومات المصدر فقط داخل الدفعة؛ أُبقي السجل الأول فقط.',
                       matched_ids=' | '.join(str(x.get('id')) for x in dupe[:10]),
                       matched_titles=' | '.join(str(x.get('title')) for x in dupe[:10]))
            audit.append(row); continue
        row.update(decision='KEEP',reason='مرشح قانوني واضح؛ لا يوجد تطابق عنواني مؤكد في المكنز أو الدفعة.')
        audit.append(row)
        final.append(item); kept_confirmed[key2].append(item)

    with (OUT/'dedup_audit.csv').open('w',encoding='utf-8-sig',newline='') as h:
        writer=csv.DictWriter(h,fieldnames=list(audit[0])); writer.writeheader(); writer.writerows(audit)
    (OUT/'final_addition_manifest.json').write_text(json.dumps(final,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    summary={
        'generated_at_utc':datetime.now(timezone.utc).isoformat(),
        'catalogue_total_before':len(current), 'screened_candidates_before_dedup':len(proposed),
        'decision_counts':dict(sorted(Counter(x['decision'] for x in audit).items())),
        'final_additions':len(final),
        'final_by_source':dict(sorted(Counter(x['source'] for x in final).items())),
        'resulting_total_if_applied':len(current)+len(final),
        'notes':[
          'لم يعدّل هذا الفحص items.json.',
          'استبعاد التكرار جرى على العنوان فقط وبالتطابق المؤكد بعد إزالة العلامات التقنية ومعلومات المصدر، مع إبقاء الأعداد والأجزاء والطبعات والاختلافات الموضوعية.',
          'لم يُحذف أو يُعدّل أي سجل قائم؛ الاستبعاد يخص مرشحات الإضافة فقط.',
        ],
    }
    (OUT/'precheck_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
