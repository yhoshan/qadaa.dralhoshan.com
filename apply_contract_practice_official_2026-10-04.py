#!/usr/bin/env python3
"""Guarded, minimal enrichment of verified contract-practice references."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ITEMS_PATH = ROOT / 'items.json'
PUBLIC_ITEMS_PATH = ROOT / 'client/public/items.json'
STATS_PATH = ROOT / 'stats.json'
PUBLIC_STATS_PATH = ROOT / 'client/public/stats.json'
CANDIDATES_PATH = ROOT / 'contract_practice_official_2026-10-04_candidates.json'

TARGET_ID = 'rabab_library_1662'
OFFICIAL_IT_URL = 'https://etimad.sa/Content/img/files/Contract2020Content/%D9%86%D9%85%D9%88%D8%B0%D8%AC%20%D8%B9%D9%82%D8%AF%20%D8%AA%D9%82%D9%86%D9%8A%D8%A9%20%D8%A7%D9%84%D9%85%D8%B9%D9%84%D9%88%D9%85%D8%A7%D8%AA.pdf'
OFFICIAL_IT_SOURCE = 'وزارة المالية السعودية — العقود والمشاريع'

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def norm(value: str) -> str:
    return ''.join(str(value).replace('أ','ا').replace('إ','ا').replace('آ','ا').replace('ى','ي').replace('ة','ه').split()).lower()

def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def rebuild_stats(items: list[dict], prior: dict) -> dict:
    stats = deepcopy(prior)
    stats['total_items'] = len(items)
    stats['categories'] = dict(Counter(str(x.get('category') or '') for x in items if str(x.get('category') or '')))
    stats['sources'] = dict(Counter(str(x.get('source') or '') for x in items if str(x.get('source') or '')))
    stats['material_types'] = dict(Counter(str(x.get('material_type') or '') for x in items if str(x.get('material_type') or '')))
    stats['file_types'] = dict(Counter(str(x.get('file_type') or '') for x in items if str(x.get('file_type') or '')))
    stats['featured_count'] = sum(bool(x.get('is_featured')) for x in items)
    stats['with_download_links'] = sum(int(x.get('download_links_count') or 0) > 0 for x in items)
    return stats

def main() -> None:
    items = json.loads(ITEMS_PATH.read_text(encoding='utf-8'))
    public_items = json.loads(PUBLIC_ITEMS_PATH.read_text(encoding='utf-8'))
    if not isinstance(items, list) or items != public_items:
        raise SystemExit('نسختا items.json غير متطابقتين قبل التنفيذ')
    before = deepcopy(items)
    stats = json.loads(STATS_PATH.read_text(encoding='utf-8'))
    if json.loads(PUBLIC_STATS_PATH.read_text(encoding='utf-8')) != stats:
        raise SystemExit('نسختا stats.json غير متطابقتين قبل التنفيذ')
    if len(items) != 45829 or stats.get('total_items') != 45829:
        raise SystemExit(f'خط أساس غير متوقع: items={len(items)} stats={stats.get("total_items")}')

    candidates = json.loads(CANDIDATES_PATH.read_text(encoding='utf-8'))
    if len(candidates) != 1:
        raise SystemExit('عدد المرشحين يجب أن يساوي 1')
    candidate = candidates[0]
    ids = {x['id'] for x in items}
    if candidate['id'] in ids:
        raise SystemExit('معرف المرشح موجود سابقاً')
    candidate_norm = norm(candidate['title'])
    if any(norm(x.get('title','')) == candidate_norm for x in items):
        raise SystemExit('عنوان المرشح موجود سابقاً بعد التطبيع')

    target = next((x for x in items if x.get('id') == TARGET_ID), None)
    if target is None or target.get('title') != 'نموذج عقد تقنية المعلومات':
        raise SystemExit('السجل المراد توثيقه غير موجود أو عنوانه تغير')
    if target.get('link_direct'):
        raise SystemExit('للسجل المراد توثيقه رابط مباشر قائم، أوقف التنفيذ')

    target['publisher'] = 'وزارة المالية السعودية / منصة اعتماد'
    target['link_direct'] = OFFICIAL_IT_URL
    target['source'] = OFFICIAL_IT_SOURCE
    target['download_links_count'] = 2
    target['integration_note'] = 'أضيف رابط رسمي علني لنموذج عقد تقنية المعلومات من وزارة المالية/منصة اعتماد، مع الإبقاء على رابط المصدر السابق.'
    items.append(candidate)

    # Guarantee that the only changed legacy record is the specifically approved quality upgrade.
    before_by = {x['id']: x for x in before}
    after_by = {x['id']: x for x in items}
    changed = sorted(k for k in before_by if before_by[k] != after_by.get(k))
    if changed != [TARGET_ID]:
        raise SystemExit(f'تغيرت سجلات قديمة غير مصرح بها: {changed}')
    if set(after_by) - set(before_by) != {candidate['id']}:
        raise SystemExit('الإضافة لا تقتصر على المرشح الرسمي الوحيد')

    updated_stats = rebuild_stats(items, stats)
    write_json(ITEMS_PATH, items)
    write_json(PUBLIC_ITEMS_PATH, items)
    write_json(STATS_PATH, updated_stats)
    write_json(PUBLIC_STATS_PATH, updated_stats)
    result = {
        'before_total': len(before),
        'after_total': len(items),
        'added_ids': [candidate['id']],
        'upgraded_ids': [TARGET_ID],
        'changed_legacy_ids': changed,
        'items_sha256': sha(ITEMS_PATH),
        'stats_sha256': sha(STATS_PATH),
    }
    write_json(ROOT / 'contract_practice_official_2026-10-04_execution.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
