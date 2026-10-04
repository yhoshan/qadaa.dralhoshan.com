#!/usr/bin/env python3
"""Delete exactly the nine user-approved IDs from the catalogue.
No title search, semantic matching, or other record modification is performed.
"""
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
BACKUP = ROOT / 'backups/political_reclassification_9_ids_2026-10-04'
MANIFEST = BACKUP / 'approved_9_removal_manifest.json'
EXECUTION = ROOT / 'political_reclassification_9_ids_2026-10-04_execution.json'

TARGETS = [
    'archive_no-law-no-rights-state',
    'great_law_5423',
    'qadi_ahdal_107698',
    'qadi_ahdal_14977',
    'qadi_ahdal_31900',
    'qadi_ahdal_53906',
    'qadi_ahdal_58456',
    'qadi_ahdal_58548',
    'qadi_ahdal_79295',
]
EXPECTED_SOURCES = {
    'archive_no-law-no-rights-state': 'أرشيف الإنترنت',
    'great_law_5423': 'المكتبة القانونية الكبرى',
    'qadi_ahdal_107698': 'مكتبة القاضي محمد الأهدل القانونية والقضائية',
    'qadi_ahdal_14977': 'مكتبة القاضي محمد الأهدل القانونية والقضائية',
    'qadi_ahdal_31900': 'مكتبة القاضي محمد الأهدل القانونية والقضائية',
    'qadi_ahdal_53906': 'مكتبة القاضي محمد الأهدل القانونية والقضائية',
    'qadi_ahdal_58456': 'مكتبة القاضي محمد الأهدل القانونية والقضائية',
    'qadi_ahdal_58548': 'مكتبة القاضي محمد الأهدل القانونية والقضائية',
    'qadi_ahdal_79295': 'مكتبة القاضي محمد الأهدل القانونية والقضائية',
}
OLD_CACHE_TOKEN = 'qadaa-mohama-professional-reclassification-2026-10-04'
NEW_CACHE_TOKEN = 'qadaa-political-reclassification-nine-removals-2026-10-04'


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def counts(values: list[str]) -> dict[str, int]:
    return dict(sorted(Counter(v for v in values if v).items(), key=lambda pair: (-pair[1], pair[0])))


def main() -> None:
    if len(TARGETS) != 9 or len(set(TARGETS)) != 9:
        raise RuntimeError('The approved target list must contain exactly nine unique IDs')
    if not BACKUP.is_dir() or not MANIFEST.is_file():
        raise RuntimeError('Required verified backup/manifest does not exist')

    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    manifest_ids = [x.get('id') for x in manifest]
    if manifest_ids != TARGETS:
        raise RuntimeError('Backup manifest does not match the approved ID-only list')

    root_items = json.loads(ITEMS.read_text(encoding='utf-8'))
    public_items = json.loads(PUBLIC_ITEMS.read_text(encoding='utf-8'))
    if root_items != public_items:
        raise RuntimeError('Root and public items must be identical before deletion')
    if len(root_items) != 45838:
        raise RuntimeError(f'Expected 45838 records before deletion; found {len(root_items)}')

    by_id = {x.get('id'): x for x in root_items}
    if len(by_id) != len(root_items):
        raise RuntimeError('Duplicate IDs found before deletion')
    missing = [ident for ident in TARGETS if ident not in by_id]
    if missing:
        raise RuntimeError(f'Requested IDs missing; refusing fallback deletion: {missing}')
    source_mismatch = [ident for ident in TARGETS if by_id[ident].get('source') != EXPECTED_SOURCES[ident]]
    if source_mismatch:
        raise RuntimeError(f'Unexpected source for approved IDs: {source_mismatch}')

    target_set = set(TARGETS)
    removed = [by_id[ident] for ident in TARGETS]
    after = [x for x in root_items if x.get('id') not in target_set]
    after_by_id = {x.get('id'): x for x in after}
    if len(after) != 45829 or len(after_by_id) != len(after):
        raise RuntimeError(f'Unexpected post-deletion record count/IDs: {len(after)}')
    if any(ident in after_by_id for ident in TARGETS):
        raise RuntimeError('At least one target ID remains after deletion')
    for ident, prior in by_id.items():
        if ident not in target_set and after_by_id.get(ident) != prior:
            raise RuntimeError(f'Non-target record changed: {ident}')

    root_stats = json.loads(STATS.read_text(encoding='utf-8'))
    public_stats = json.loads(PUBLIC_STATS.read_text(encoding='utf-8'))
    if root_stats != public_stats:
        raise RuntimeError('Root and public stats must be identical before deletion')
    root_stats['total_items'] = len(after)
    if 'total' in root_stats:
        root_stats['total'] = len(after)
    root_stats['categories'] = counts([str(x.get('category') or '') for x in after])
    root_stats['sources'] = counts([str(x.get('source') or '') for x in after])
    root_stats['material_types'] = counts([str(x.get('material_type') or '') for x in after])
    root_stats['file_types'] = counts([str(x.get('file_type') or '') for x in after])
    root_stats['featured_count'] = sum(bool(x.get('is_featured')) for x in after)
    root_stats['with_download_links'] = sum(int(x.get('download_links_count') or 0) > 0 for x in after)

    hook = HOOK.read_text(encoding='utf-8')
    if hook.count(OLD_CACHE_TOKEN) != 2:
        raise RuntimeError('Expected the existing cache token exactly twice in useItems.ts')

    write_json(ITEMS, after)
    write_json(PUBLIC_ITEMS, after)
    write_json(STATS, root_stats)
    write_json(PUBLIC_STATS, root_stats)
    HOOK.write_text(hook.replace(OLD_CACHE_TOKEN, NEW_CACHE_TOKEN), encoding='utf-8')

    execution = {
        'operation': 'user_approved_id_only_deletion',
        'executed_at_utc': datetime.now(timezone.utc).isoformat(),
        'requested_count': 9,
        'found_count': 9,
        'removed_count': 9,
        'before_total': len(root_items),
        'after_total': len(after),
        'removed_ids': TARGETS,
        'removed_records': [
            {'id': x.get('id'), 'title': x.get('title'), 'source': x.get('source')}
            for x in removed
        ],
        'removed_by_source': dict(Counter(str(x.get('source') or '') for x in removed)),
        'cache_token': NEW_CACHE_TOKEN,
        'items_sha256': digest(ITEMS),
        'public_items_sha256': digest(PUBLIC_ITEMS),
        'stats_sha256_before_hero_refresh': digest(STATS),
        'public_stats_sha256_before_hero_refresh': digest(PUBLIC_STATS),
        'non_target_records_preserved': True,
    }
    write_json(EXECUTION, execution)
    print(json.dumps(execution, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
