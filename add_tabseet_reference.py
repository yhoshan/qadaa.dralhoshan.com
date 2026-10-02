#!/usr/bin/env python3
"""Add the one verified Tabseet reference and rebuild derived data."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ITEMS_PATH = ROOT / 'items.json'
PUBLIC_ITEMS_PATH = ROOT / 'client/public/items.json'
STATS_PATH = ROOT / 'stats.json'
PUBLIC_STATS_PATH = ROOT / 'client/public/stats.json'
HOOK_PATH = ROOT / 'client/src/hooks/useItems.ts'
EXECUTION_PATH = ROOT / 'tabseet_reference_2026-10-02_execution.json'
EXPECTED_BEFORE_TOTAL = 17618
CACHE_TOKEN = 'qadaa-tabseet-reference-2026-10-02'

RECORD = {
    'id': 'tabseet_civil_transactions_001',
    'title': 'تبسيط نظام المعاملات المدنية: فهرس وشرح ودفوع وحاسبة مدد',
    'author': '',
    'investigator': '',
    'publisher': 'منصة تبسيط',
    'year': '',
    'link_telegram': '',
    'link_drive': '',
    'link_direct': 'https://saudalbazei.com/tabseet/',
    'source': 'منصة تبسيط',
    'category': 'الأنظمة والتشريعات',
    'material_type': 'شرح',
    'file_type': 'رابط',
    'file_size': '',
    'pages_count': '',
    'is_featured': False,
    'download_links_count': 1,
}


def sorted_counts(values: Counter[str]) -> dict[str, int]:
    return dict(sorted(values.items(), key=lambda pair: (-pair[1], pair[0])))


def normalize(value: str) -> str:
    value = unicodedata.normalize('NFKC', value).lower()
    value = re.sub(r'[\u064B-\u065F\u0670ـ]', '', value)
    value = re.sub('[إأآٱ]', 'ا', value).replace('ى', 'ي').replace('ة', 'ه')
    value = re.sub(r'[^\w\s]', ' ', value)
    return re.sub(r'\s+', ' ', value).strip()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main() -> None:
    items = json.loads(ITEMS_PATH.read_text(encoding='utf-8'))
    if not isinstance(items, list):
        raise RuntimeError('items.json must be a list')
    if len(items) != EXPECTED_BEFORE_TOTAL:
        raise RuntimeError(f'Expected {EXPECTED_BEFORE_TOTAL} items, found {len(items)}')
    if any(item.get('id') == RECORD['id'] for item in items):
        raise RuntimeError(f"Duplicate id: {RECORD['id']}")
    if any(str(item.get('link_direct') or '') == RECORD['link_direct'] for item in items):
        raise RuntimeError('Tabseet direct link is already present')
    title_norm = normalize(RECORD['title'])
    if any(normalize(str(item.get('title') or '')) == title_norm for item in items):
        raise RuntimeError('Tabseet reference title is already present after normalization')

    before_by_id = {item['id']: item for item in items}
    items.append(RECORD)
    after_by_id = {item['id']: item for item in items}
    if set(after_by_id) - set(before_by_id) != {RECORD['id']}:
        raise RuntimeError('Unexpected IDs would be added')

    expected_after_total = EXPECTED_BEFORE_TOTAL + 1
    if len(items) != expected_after_total or len(after_by_id) != expected_after_total:
        raise RuntimeError('Item total or ID uniqueness failure')

    stats = json.loads(STATS_PATH.read_text(encoding='utf-8'))
    stats['total_items'] = expected_after_total
    if 'total' in stats:
        stats['total'] = expected_after_total
    stats['categories'] = sorted_counts(Counter(str(item.get('category') or '') for item in items if item.get('category')))
    stats['sources'] = sorted_counts(Counter(str(item.get('source') or '') for item in items if item.get('source')))
    stats['material_types'] = sorted_counts(Counter(str(item.get('material_type') or '') for item in items if item.get('material_type')))
    stats['file_types'] = sorted_counts(Counter(str(item.get('file_type') or '') for item in items if item.get('file_type')))
    stats['featured_count'] = sum(1 for item in items if item.get('is_featured'))
    stats['with_download_links'] = sum(1 for item in items if int(item.get('download_links_count') or 0) > 0)

    write_json(ITEMS_PATH, items)
    write_json(PUBLIC_ITEMS_PATH, items)
    write_json(STATS_PATH, stats)
    write_json(PUBLIC_STATS_PATH, stats)

    hook = HOOK_PATH.read_text(encoding='utf-8')
    old_token = 'qadaa-drive-legal-links-2026-10-01'
    if old_token not in hook:
        raise RuntimeError('Expected prior cache token not found in useItems.ts')
    HOOK_PATH.write_text(hook.replace(old_token, CACHE_TOKEN), encoding='utf-8')

    execution = {
        'operation': 'add_single_tabseet_reference',
        'executed_at': datetime.now(timezone.utc).isoformat(),
        'before_total': EXPECTED_BEFORE_TOTAL,
        'added_id': RECORD['id'],
        'added_title': RECORD['title'],
        'after_total': expected_after_total,
        'cache_token': CACHE_TOKEN,
        'items_sha256': hashlib.sha256(ITEMS_PATH.read_bytes()).hexdigest(),
        'stats_sha256': hashlib.sha256(STATS_PATH.read_bytes()).hexdigest(),
    }
    write_json(EXECUTION_PATH, execution)
    print(json.dumps(execution, ensure_ascii=False))


if __name__ == '__main__':
    main()
