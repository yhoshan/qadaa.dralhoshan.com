#!/usr/bin/env python3
"""Add verified, nonduplicate recent KSU law-journal articles only."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ITEMS = ROOT / 'items.json'
PUBLIC_ITEMS = ROOT / 'client/public/items.json'
STATS = ROOT / 'stats.json'
PUBLIC_STATS = ROOT / 'client/public/stats.json'
HOOK = ROOT / 'client/src/hooks/useItems.ts'
CANDIDATES = ROOT / 'ksu_law_journal_recent_2026-10-03_candidates.json'
PRECHECK = ROOT / 'ksu_law_journal_recent_2026-10-03_precheck.json'
EXECUTION = ROOT / 'ksu_law_journal_recent_2026-10-03_execution.json'
EXPECTED_BEFORE = 20001
EXPECTED_CANDIDATES = 56
EXPECTED_EXCLUDED_IDS = {'ksu_lps_v34_i1_04', 'ksu_lps_v34_i1_06'}
EXPECTED_ADD = 54
CACHE_TOKEN_OLD = 'qadaa-three-channels-20001-2026-10-03'
CACHE_TOKEN_NEW = 'qadaa-ksu-law-journal-recent-2026-10-03'
STANDARD_FIELDS = (
    'id', 'title', 'author', 'investigator', 'publisher', 'year',
    'link_telegram', 'link_drive', 'link_direct', 'source', 'category',
    'material_type', 'file_type', 'file_size', 'pages_count', 'is_featured',
    'download_links_count',
)


def normalized_title(value: str) -> str:
    value = unicodedata.normalize('NFKD', str(value or ''))
    value = ''.join(ch for ch in value if not unicodedata.combining(ch))
    value = value.translate(str.maketrans({'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ى': 'ي', 'ؤ': 'و', 'ئ': 'ي'}))
    value = re.sub(r'[^\w\s]', ' ', value)
    return re.sub(r'\s+', ' ', value).strip().lower()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sorted_counts(values: Counter[str]) -> dict[str, int]:
    return dict(sorted(values.items(), key=lambda pair: (-pair[1], pair[0])))


def main() -> None:
    items = json.loads(ITEMS.read_text(encoding='utf-8'))
    public_items = json.loads(PUBLIC_ITEMS.read_text(encoding='utf-8'))
    candidates = json.loads(CANDIDATES.read_text(encoding='utf-8'))
    precheck = json.loads(PRECHECK.read_text(encoding='utf-8'))
    if not isinstance(items, list) or not isinstance(public_items, list) or not isinstance(candidates, list):
        raise RuntimeError('Expected list JSON for items and candidates')
    if items != public_items:
        raise RuntimeError('Root and public item data differ before integration')
    if len(items) != EXPECTED_BEFORE:
        raise RuntimeError(f'Expected {EXPECTED_BEFORE} records before addition; found {len(items)}')
    if len(candidates) != EXPECTED_CANDIDATES:
        raise RuntimeError(f'Expected {EXPECTED_CANDIDATES} candidates; found {len(candidates)}')

    precheck_excluded = {entry['candidate']['id'] for entry in precheck.get('exact_duplicates', [])}
    if precheck_excluded != EXPECTED_EXCLUDED_IDS or precheck.get('near_match_count') != 0:
        raise RuntimeError('Duplicate precheck differs from the reviewed two-record exact-match set')

    existing_ids = {str(x.get('id', '')) for x in items}
    existing_titles = {normalized_title(x.get('title', '')) for x in items}
    candidate_ids = [str(x.get('id', '')) for x in candidates]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise RuntimeError('Candidate IDs are not unique')
    if set(candidate_ids) & existing_ids:
        raise RuntimeError('Candidate ID collision with existing data')

    records = []
    for candidate in candidates:
        if candidate['id'] in EXPECTED_EXCLUDED_IDS:
            if normalized_title(candidate['title']) not in existing_titles:
                raise RuntimeError(f'Expected exact duplicate title is absent: {candidate["id"]}')
            continue
        record = {field: candidate.get(field) for field in STANDARD_FIELDS}
        if normalized_title(record['title']) in existing_titles:
            raise RuntimeError(f'Unexpected duplicate title: {record["title"]}')
        if record['source'] != 'مجلة جامعة الملك سعود للحقوق والعلوم السياسية':
            raise RuntimeError('Source changed unexpectedly')
        if record['category'] != 'البحوث القانونية والسياسية' or record['material_type'] != 'بحث':
            raise RuntimeError('Classification changed unexpectedly')
        if not str(record['link_direct']).startswith('https://clps.ksu.edu.sa/'):
            raise RuntimeError('Non-official journal link detected')
        records.append(record)

    if len(records) != EXPECTED_ADD:
        raise RuntimeError(f'Expected {EXPECTED_ADD} records to add; found {len(records)}')
    before_by_id = {x['id']: x for x in items}
    items_after = items + records
    after_by_id = {x['id']: x for x in items_after}
    if len(items_after) != EXPECTED_BEFORE + EXPECTED_ADD or len(after_by_id) != len(items_after):
        raise RuntimeError('Total or ID uniqueness check failed after addition')
    if set(after_by_id) - set(before_by_id) != {x['id'] for x in records}:
        raise RuntimeError('Unexpected record IDs would be added')
    if any(before_by_id[item_id] != after_by_id[item_id] for item_id in before_by_id):
        raise RuntimeError('Existing item data would change')

    stats = json.loads(STATS.read_text(encoding='utf-8'))
    total = len(items_after)
    stats['total_items'] = total
    if 'total' in stats:
        stats['total'] = total
    stats['categories'] = sorted_counts(Counter(str(x.get('category') or '') for x in items_after if x.get('category')))
    stats['sources'] = sorted_counts(Counter(str(x.get('source') or '') for x in items_after if x.get('source')))
    stats['material_types'] = sorted_counts(Counter(str(x.get('material_type') or '') for x in items_after if x.get('material_type')))
    stats['file_types'] = sorted_counts(Counter(str(x.get('file_type') or '') for x in items_after if x.get('file_type')))
    stats['featured_count'] = sum(bool(x.get('is_featured')) for x in items_after)
    stats['with_download_links'] = sum(int(x.get('download_links_count') or 0) > 0 for x in items_after)

    hook = HOOK.read_text(encoding='utf-8')
    if CACHE_TOKEN_OLD not in hook:
        raise RuntimeError(f'Expected cache token {CACHE_TOKEN_OLD!r} not found')

    write_json(ITEMS, items_after)
    write_json(PUBLIC_ITEMS, items_after)
    write_json(STATS, stats)
    write_json(PUBLIC_STATS, stats)
    HOOK.write_text(hook.replace(CACHE_TOKEN_OLD, CACHE_TOKEN_NEW), encoding='utf-8')

    result = {
        'operation': 'add_ksu_law_journal_recent_articles',
        'executed_at': datetime.now(timezone.utc).isoformat(),
        'before_total': EXPECTED_BEFORE,
        'candidate_total': EXPECTED_CANDIDATES,
        'excluded_existing_exact_duplicates': sorted(EXPECTED_EXCLUDED_IDS),
        'added_total': EXPECTED_ADD,
        'after_total': total,
        'cache_token': CACHE_TOKEN_NEW,
        'items_sha256': hashlib.sha256(ITEMS.read_bytes()).hexdigest(),
        'stats_sha256': hashlib.sha256(STATS.read_bytes()).hexdigest(),
    }
    write_json(EXECUTION, result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
