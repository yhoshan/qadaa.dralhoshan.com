#!/usr/bin/env python3
"""Add the 721 stable Tabseet article anchors and rebuild derived data."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ITEMS = ROOT / 'items.json'
PUBLIC_ITEMS = ROOT / 'client/public/items.json'
STATS = ROOT / 'stats.json'
PUBLIC_STATS = ROOT / 'client/public/stats.json'
HOOK = ROOT / 'client/src/hooks/useItems.ts'
CANDIDATES = ROOT / 'tabseet_civil_articles_2026-10-02_candidates.json'
EXECUTION = ROOT / 'tabseet_civil_articles_2026-10-02_execution.json'
EXPECTED_BEFORE = 17619
EXPECTED_ADD = 721
CACHE_TOKEN_OLD = 'qadaa-tabseet-reference-2026-10-02'
CACHE_TOKEN_NEW = 'qadaa-tabseet-civil-articles-2026-10-02'
STANDARD_FIELDS = (
    'id', 'title', 'author', 'investigator', 'publisher', 'year',
    'link_telegram', 'link_drive', 'link_direct', 'source', 'category',
    'material_type', 'file_type', 'file_size', 'pages_count', 'is_featured',
    'download_links_count',
)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sorted_counts(values: Counter[str]) -> dict[str, int]:
    return dict(sorted(values.items(), key=lambda pair: (-pair[1], pair[0])))


def main() -> None:
    items = json.loads(ITEMS.read_text(encoding='utf-8'))
    candidates = json.loads(CANDIDATES.read_text(encoding='utf-8'))
    if not isinstance(items, list) or not isinstance(candidates, list):
        raise RuntimeError('Expected list JSON for items and candidates')
    if len(items) != EXPECTED_BEFORE:
        raise RuntimeError(f'Expected {EXPECTED_BEFORE} records before addition; found {len(items)}')
    if len(candidates) != EXPECTED_ADD:
        raise RuntimeError(f'Expected {EXPECTED_ADD} candidate records; found {len(candidates)}')

    records = [{field: candidate.get(field) for field in STANDARD_FIELDS} for candidate in candidates]
    ids = [str(x['id']) for x in records]
    links = [str(x['link_direct']) for x in records]
    if len(ids) != len(set(ids)) or len(links) != len(set(links)):
        raise RuntimeError('Candidate IDs or direct links contain duplicates')
    if set(ids) & {str(x.get('id', '')) for x in items}:
        raise RuntimeError('Candidate ID collision with existing records')
    existing_links = {
        str(value)
        for item in items
        for value in (item.get('link_direct'), item.get('link_drive'), item.get('link_telegram'))
        if value
    }
    if set(links) & existing_links:
        raise RuntimeError('Candidate direct link collision with existing records')
    if any(x['source'] != 'منصة تبسيط' or x['category'] != 'الأنظمة والتشريعات' or x['material_type'] != 'شرح' for x in records):
        raise RuntimeError('Candidate classification changed unexpectedly')

    before_by_id = {x['id']: x for x in items}
    items_after = items + records
    after_by_id = {x['id']: x for x in items_after}
    expected_after = EXPECTED_BEFORE + EXPECTED_ADD
    if len(items_after) != expected_after or len(after_by_id) != expected_after:
        raise RuntimeError('Total or ID uniqueness check failed after addition')
    if set(after_by_id) - set(before_by_id) != set(ids):
        raise RuntimeError('Unexpected record IDs would be added')
    if any(before_by_id[item_id] != after_by_id[item_id] for item_id in before_by_id):
        raise RuntimeError('Existing item data would change')

    stats = json.loads(STATS.read_text(encoding='utf-8'))
    stats['total_items'] = expected_after
    if 'total' in stats:
        stats['total'] = expected_after
    stats['categories'] = sorted_counts(Counter(str(x.get('category') or '') for x in items_after if x.get('category')))
    stats['sources'] = sorted_counts(Counter(str(x.get('source') or '') for x in items_after if x.get('source')))
    stats['material_types'] = sorted_counts(Counter(str(x.get('material_type') or '') for x in items_after if x.get('material_type')))
    stats['file_types'] = sorted_counts(Counter(str(x.get('file_type') or '') for x in items_after if x.get('file_type')))
    stats['featured_count'] = sum(1 for x in items_after if x.get('is_featured'))
    stats['with_download_links'] = sum(1 for x in items_after if int(x.get('download_links_count') or 0) > 0)

    write_json(ITEMS, items_after)
    write_json(PUBLIC_ITEMS, items_after)
    write_json(STATS, stats)
    write_json(PUBLIC_STATS, stats)

    hook = HOOK.read_text(encoding='utf-8')
    if CACHE_TOKEN_OLD not in hook:
        raise RuntimeError(f'Expected cache token {CACHE_TOKEN_OLD!r} not found')
    HOOK.write_text(hook.replace(CACHE_TOKEN_OLD, CACHE_TOKEN_NEW), encoding='utf-8')

    result = {
        'operation': 'add_tabseet_civil_articles',
        'executed_at': datetime.now(timezone.utc).isoformat(),
        'before_total': EXPECTED_BEFORE,
        'added_total': EXPECTED_ADD,
        'after_total': expected_after,
        'first_added_id': records[0]['id'],
        'last_added_id': records[-1]['id'],
        'cache_token': CACHE_TOKEN_NEW,
        'items_sha256': hashlib.sha256(ITEMS.read_bytes()).hexdigest(),
        'stats_sha256': hashlib.sha256(STATS.read_bytes()).hexdigest(),
    }
    write_json(EXECUTION, result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
