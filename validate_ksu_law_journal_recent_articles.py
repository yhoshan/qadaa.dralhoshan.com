#!/usr/bin/env python3
"""Validate the 54-record KSU law journal integration without modifying data."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / 'backups/ksu_law_journal_recent_2026-10-03'
CANDIDATES = ROOT / 'ksu_law_journal_recent_2026-10-03_candidates.json'
EXCLUDED = {'ksu_lps_v34_i1_04', 'ksu_lps_v34_i1_06'}
EXPECTED_ADDED = 54
EXPECTED_TOTAL = 20055
SOURCE = 'مجلة جامعة الملك سعود للحقوق والعلوم السياسية'


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> None:
    before = load(BACKUP / 'items_before.json')
    items = load(ROOT / 'items.json')
    public_items = load(ROOT / 'client/public/items.json')
    stats = load(ROOT / 'stats.json')
    public_stats = load(ROOT / 'client/public/stats.json')
    candidates = load(CANDIDATES)
    assert len(before) == 20001
    assert len(items) == EXPECTED_TOTAL
    assert items == public_items
    assert stats == public_stats
    assert stats['total_items'] == EXPECTED_TOTAL
    ids = [x.get('id') for x in items]
    assert len(ids) == len(set(ids))
    before_by_id = {x['id']: x for x in before}
    after_by_id = {x['id']: x for x in items}
    assert all(after_by_id[key] == value for key, value in before_by_id.items())
    expected_new = {x['id'] for x in candidates} - EXCLUDED
    actual_new = set(after_by_id) - set(before_by_id)
    assert actual_new == expected_new
    assert len(actual_new) == EXPECTED_ADDED
    assert not (EXCLUDED & actual_new)
    excluded_titles = {x['title'] for x in candidates if x['id'] in EXCLUDED}
    before_titles = {x['title'] for x in before}
    assert excluded_titles <= before_titles
    new_records = [after_by_id[x] for x in sorted(actual_new)]
    assert all(x['source'] == SOURCE for x in new_records)
    assert all(x['link_direct'].startswith('https://clps.ksu.edu.sa/') for x in new_records)
    assert all(x['material_type'] == 'بحث' and x['category'] == 'البحوث القانونية والسياسية' for x in new_records)
    assert sum(x.get('source') == SOURCE for x in items) == EXPECTED_ADDED
    assert stats['sources'].get(SOURCE) == EXPECTED_ADDED
    assert stats['qadaa_count'] + stats['nizam_count'] + stats['mohama_count'] == EXPECTED_TOTAL
    hook = (ROOT / 'client/src/hooks/useItems.ts').read_text(encoding='utf-8')
    assert 'qadaa-ksu-law-journal-recent-2026-10-03' in hook
    result = {
        'before_total': len(before),
        'added_total': len(actual_new),
        'after_total': len(items),
        'source_count': stats['sources'][SOURCE],
        'duplicate_ids': len(ids) - len(set(ids)),
        'items_sha256': hashlib.sha256((ROOT / 'items.json').read_bytes()).hexdigest(),
        'stats_sha256': hashlib.sha256((ROOT / 'stats.json').read_bytes()).hexdigest(),
        'result': 'passed',
    }
    (ROOT / 'ksu_law_journal_recent_2026-10-03_validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
