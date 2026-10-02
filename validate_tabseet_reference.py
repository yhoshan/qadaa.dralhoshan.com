#!/usr/bin/env python3
"""Validate the single Tabseet reference integration."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / 'backups/tabseet_reference_2026-10-02'
ITEMS = ROOT / 'items.json'
PUBLIC_ITEMS = ROOT / 'client/public/items.json'
STATS = ROOT / 'stats.json'
PUBLIC_STATS = ROOT / 'client/public/stats.json'
HOOK = ROOT / 'client/src/hooks/useItems.ts'
EXECUTION = ROOT / 'tabseet_reference_2026-10-02_execution.json'
VALIDATION = ROOT / 'tabseet_reference_2026-10-02_validation.json'
TARGET = 'tabseet_civil_transactions_001'
EXPECTED_BEFORE = 17618
EXPECTED_AFTER = 17619
CACHE_TOKEN = 'qadaa-tabseet-reference-2026-10-02'


def sort_counts(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted(counter.items(), key=lambda pair: (-pair[1], pair[0])))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    before = json.loads((BACKUP / 'items.before.json').read_text(encoding='utf-8'))
    after = json.loads(ITEMS.read_text(encoding='utf-8'))
    public_after_text = PUBLIC_ITEMS.read_text(encoding='utf-8')
    after_text = ITEMS.read_text(encoding='utf-8')
    stats = json.loads(STATS.read_text(encoding='utf-8'))
    public_stats_text = PUBLIC_STATS.read_text(encoding='utf-8')
    stats_text = STATS.read_text(encoding='utf-8')
    execution = json.loads(EXECUTION.read_text(encoding='utf-8'))

    assert len(before) == EXPECTED_BEFORE
    assert len(after) == EXPECTED_AFTER
    assert after_text == public_after_text
    assert stats_text == public_stats_text
    assert stats.get('total_items') == EXPECTED_AFTER
    assert stats.get('total') == EXPECTED_AFTER
    assert sum(int(stats.get(key, 0)) for key in ('qadaa_count', 'nizam_count', 'mohama_count')) == EXPECTED_AFTER
    assert CACHE_TOKEN in HOOK.read_text(encoding='utf-8')
    assert execution.get('before_total') == EXPECTED_BEFORE
    assert execution.get('after_total') == EXPECTED_AFTER
    assert execution.get('added_id') == TARGET

    before_by_id = {item['id']: item for item in before}
    after_by_id = {item['id']: item for item in after}
    ids = [item['id'] for item in after]
    assert len(ids) == len(set(ids))
    assert set(after_by_id) - set(before_by_id) == {TARGET}
    assert not (set(before_by_id) - set(after_by_id))
    assert all(before_by_id[item_id] == after_by_id[item_id] for item_id in before_by_id)
    target = after_by_id[TARGET]
    assert target['link_direct'] == 'https://saudalbazei.com/tabseet/'
    assert target['source'] == 'منصة تبسيط'
    assert target['category'] == 'الأنظمة والتشريعات'
    assert target['material_type'] == 'شرح'
    assert target['download_links_count'] == 1
    assert not target['link_telegram'] and not target['link_drive']

    assert stats['categories'] == sort_counts(Counter(str(item.get('category') or '') for item in after if item.get('category')))
    assert stats['sources'] == sort_counts(Counter(str(item.get('source') or '') for item in after if item.get('source')))
    assert stats['material_types'] == sort_counts(Counter(str(item.get('material_type') or '') for item in after if item.get('material_type')))
    assert stats['file_types'] == sort_counts(Counter(str(item.get('file_type') or '') for item in after if item.get('file_type')))
    assert stats['featured_count'] == sum(1 for item in after if item.get('is_featured'))
    assert stats['with_download_links'] == sum(1 for item in after if int(item.get('download_links_count') or 0) > 0)

    result = {
        'result': 'passed',
        'before_total': EXPECTED_BEFORE,
        'added_total': 1,
        'after_total': EXPECTED_AFTER,
        'target_id': TARGET,
        'unchanged_old_records': len(before_by_id),
        'old_records_missing': 0,
        'old_records_changed': 0,
        'duplicate_id_count': len(ids) - len(set(ids)),
        'main_public_items_match': True,
        'main_public_stats_match': True,
        'cache_token': CACHE_TOKEN,
        'hero_counts': {key: stats.get(key) for key in ('qadaa_count', 'nizam_count', 'mohama_count')},
        'files_sha256': {
            'items.json': digest(ITEMS),
            'client/public/items.json': digest(PUBLIC_ITEMS),
            'stats.json': digest(STATS),
            'client/public/stats.json': digest(PUBLIC_STATS),
        },
    }
    VALIDATION.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
