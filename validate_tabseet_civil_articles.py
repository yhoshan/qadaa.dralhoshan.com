#!/usr/bin/env python3
"""Validate the 721-record Tabseet civil articles integration."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / 'backups/tabseet_civil_articles_2026-10-02'
ITEMS = ROOT / 'items.json'
PUBLIC_ITEMS = ROOT / 'client/public/items.json'
STATS = ROOT / 'stats.json'
PUBLIC_STATS = ROOT / 'client/public/stats.json'
HOOK = ROOT / 'client/src/hooks/useItems.ts'
CANDIDATES = ROOT / 'tabseet_civil_articles_2026-10-02_candidates.json'
EXECUTION = ROOT / 'tabseet_civil_articles_2026-10-02_execution.json'
VALIDATION = ROOT / 'tabseet_civil_articles_2026-10-02_validation.json'
EXPECTED_BEFORE = 17619
EXPECTED_ADD = 721
EXPECTED_AFTER = 18340
CACHE_TOKEN = 'qadaa-tabseet-civil-articles-2026-10-02'
STANDARD_FIELDS = {
    'id', 'title', 'author', 'investigator', 'publisher', 'year',
    'link_telegram', 'link_drive', 'link_direct', 'source', 'category',
    'material_type', 'file_type', 'file_size', 'pages_count', 'is_featured',
    'download_links_count',
}


def sorted_counts(values: Counter[str]) -> dict[str, int]:
    return dict(sorted(values.items(), key=lambda pair: (-pair[1], pair[0])))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    before = json.loads((BACKUP / 'main/items.json').read_text(encoding='utf-8'))
    after = json.loads(ITEMS.read_text(encoding='utf-8'))
    public_after_text = PUBLIC_ITEMS.read_text(encoding='utf-8')
    after_text = ITEMS.read_text(encoding='utf-8')
    stats = json.loads(STATS.read_text(encoding='utf-8'))
    public_stats_text = PUBLIC_STATS.read_text(encoding='utf-8')
    stats_text = STATS.read_text(encoding='utf-8')
    candidates = json.loads(CANDIDATES.read_text(encoding='utf-8'))
    execution = json.loads(EXECUTION.read_text(encoding='utf-8'))

    assert len(before) == EXPECTED_BEFORE
    assert len(candidates) == EXPECTED_ADD
    assert len(after) == EXPECTED_AFTER
    assert after_text == public_after_text
    assert stats_text == public_stats_text
    assert stats['total_items'] == EXPECTED_AFTER
    assert stats.get('total') == EXPECTED_AFTER
    assert sum(int(stats.get(key, 0)) for key in ('qadaa_count', 'nizam_count', 'mohama_count')) == EXPECTED_AFTER
    assert CACHE_TOKEN in HOOK.read_text(encoding='utf-8')
    assert execution['before_total'] == EXPECTED_BEFORE
    assert execution['added_total'] == EXPECTED_ADD
    assert execution['after_total'] == EXPECTED_AFTER

    before_by_id = {item['id']: item for item in before}
    after_by_id = {item['id']: item for item in after}
    added_ids = set(after_by_id) - set(before_by_id)
    expected_ids = {candidate['id'] for candidate in candidates}
    assert added_ids == expected_ids
    assert not (set(before_by_id) - set(after_by_id))
    assert all(before_by_id[item_id] == after_by_id[item_id] for item_id in before_by_id)
    assert len(after_by_id) == len(after)

    for candidate in candidates:
        actual = after_by_id[candidate['id']]
        expected = {field: candidate.get(field) for field in STANDARD_FIELDS}
        assert actual == expected
        assert actual['source'] == 'منصة تبسيط'
        assert actual['category'] == 'الأنظمة والتشريعات'
        assert actual['material_type'] == 'شرح'
        assert actual['file_type'] == 'رابط'
        assert actual['download_links_count'] == 1
        assert actual['link_direct'].startswith('https://saudalbazei.com/tabseet/#a')
        assert not actual['link_telegram'] and not actual['link_drive']

    assert stats['categories'] == sorted_counts(Counter(str(x.get('category') or '') for x in after if x.get('category')))
    assert stats['sources'] == sorted_counts(Counter(str(x.get('source') or '') for x in after if x.get('source')))
    assert stats['material_types'] == sorted_counts(Counter(str(x.get('material_type') or '') for x in after if x.get('material_type')))
    assert stats['file_types'] == sorted_counts(Counter(str(x.get('file_type') or '') for x in after if x.get('file_type')))
    assert stats['featured_count'] == sum(1 for x in after if x.get('is_featured'))
    assert stats['with_download_links'] == sum(1 for x in after if int(x.get('download_links_count') or 0) > 0)
    assert stats['sources']['منصة تبسيط'] == 722
    # توجد مادة «تبسيط» المرجعية السابقة ضمن نوع «شرح» قبل هذه الدفعة.
    assert stats['material_types']['شرح'] == 821

    result = {
        'result': 'passed',
        'before_total': EXPECTED_BEFORE,
        'added_total': EXPECTED_ADD,
        'after_total': EXPECTED_AFTER,
        'existing_records_unchanged': EXPECTED_BEFORE,
        'missing_existing_records': 0,
        'changed_existing_records': 0,
        'added_records': len(added_ids),
        'duplicate_id_count': len(after) - len(after_by_id),
        'main_public_items_match': True,
        'main_public_stats_match': True,
        'tabseet_source_count': stats['sources']['منصة تبسيط'],
        'hero_counts': {key: stats.get(key) for key in ('qadaa_count', 'nizam_count', 'mohama_count')},
        'cache_token': CACHE_TOKEN,
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
