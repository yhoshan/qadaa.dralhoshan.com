#!/usr/bin/env python3
"""Validate the Drive title-and-link-only integration."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / 'backups/drive_legal_links_2026-10-01'
ITEMS_PATH = ROOT / 'items.json'
PUBLIC_ITEMS_PATH = ROOT / 'client/public/items.json'
STATS_PATH = ROOT / 'stats.json'
PUBLIC_STATS_PATH = ROOT / 'client/public/stats.json'
ACCEPTED_PATH = ROOT / 'drive_legal_links_2026-10-01_accepted.json'
EXECUTION_PATH = ROOT / 'drive_legal_links_2026-10-01_execution.json'
VALIDATION_PATH = ROOT / 'drive_legal_links_2026-10-01_validation.json'

EXPECTED_BEFORE = 17481
EXPECTED_ADDED = 137
EXPECTED_AFTER = 17618


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    before_items = json.loads((BACKUP / 'items.before.json').read_text(encoding='utf-8'))
    after_items = json.loads(ITEMS_PATH.read_text(encoding='utf-8'))
    public_items_text = PUBLIC_ITEMS_PATH.read_text(encoding='utf-8')
    after_items_text = ITEMS_PATH.read_text(encoding='utf-8')
    stats = json.loads(STATS_PATH.read_text(encoding='utf-8'))
    public_stats_text = PUBLIC_STATS_PATH.read_text(encoding='utf-8')
    stats_text = STATS_PATH.read_text(encoding='utf-8')
    accepted = json.loads(ACCEPTED_PATH.read_text(encoding='utf-8'))
    execution = json.loads(EXECUTION_PATH.read_text(encoding='utf-8'))

    assert len(before_items) == EXPECTED_BEFORE, f'إجمالي النسخة الاحتياطية غير صحيح: {len(before_items)}'
    assert len(after_items) == EXPECTED_AFTER, f'إجمالي لاحق غير صحيح: {len(after_items)}'
    assert len(accepted) == EXPECTED_ADDED, f'عدد الإضافات المعتمد غير صحيح: {len(accepted)}'
    assert after_items_text == public_items_text, 'items.json لا يطابق client/public/items.json'
    assert stats_text == public_stats_text, 'stats.json لا يطابق client/public/stats.json'
    assert stats.get('total_items') == EXPECTED_AFTER, 'total_items لا يطابق الإجمالي'
    assert stats.get('total') == EXPECTED_AFTER, 'total لا يطابق الإجمالي'
    assert sum(int(stats.get(key, 0)) for key in ('qadaa_count', 'nizam_count', 'mohama_count')) == EXPECTED_AFTER, 'مجموع بطاقات Hero لا يطابق الإجمالي'
    assert execution.get('before_total') == EXPECTED_BEFORE and execution.get('added_total') == EXPECTED_ADDED and execution.get('after_total') == EXPECTED_AFTER, 'سجل التنفيذ غير مطابق'

    before_by_id = {item['id']: item for item in before_items}
    after_by_id = {item['id']: item for item in after_items}
    accepted_by_id = {item['id']: {key: value for key, value in item.items() if not key.startswith('_')} for item in accepted}
    added_ids = set(after_by_id) - set(before_by_id)
    missing_old_ids = set(before_by_id) - set(after_by_id)
    changed_old_ids = [item_id for item_id in before_by_id if before_by_id[item_id] != after_by_id[item_id]]

    assert not missing_old_ids, f'فقدت سجلات قديمة: {sorted(missing_old_ids)[:10]}'
    assert not changed_old_ids, f'تغيرت سجلات قديمة: {changed_old_ids[:10]}'
    assert added_ids == set(accepted_by_id), 'السجلات الجديدة لا تطابق قائمة القبول'
    assert all(after_by_id[item_id] == accepted_by_id[item_id] for item_id in added_ids), 'أحد السجلات المضافة لا يطابق قائمة القبول'

    ids = [item['id'] for item in after_items]
    assert len(ids) == len(set(ids)), 'توجد معرّفات مكررة'
    added = [after_by_id[item_id] for item_id in sorted(added_ids)]
    assert all(item.get('link_drive', '').startswith('https://drive.google.com/file/d/') for item in added), 'رابط Drive مفقود أو غير صالح'
    assert all(not item.get('link_telegram') and not item.get('link_direct') for item in added), 'وجد رابط غير Drive في الإضافات'
    assert all(int(item.get('download_links_count') or 0) == 1 for item in added), 'عداد روابط غير صحيح في الإضافات'

    expected_counts = {
        'categories': Counter(item.get('category') for item in after_items if item.get('category')),
        'sources': Counter(item.get('source') for item in after_items if item.get('source')),
        'material_types': Counter(item.get('material_type') for item in after_items if item.get('material_type')),
        'file_types': Counter(item.get('file_type') for item in after_items if item.get('file_type')),
    }
    for field, expected in expected_counts.items():
        actual = stats.get(field, {})
        assert actual == dict(sorted(expected.items(), key=lambda pair: (-pair[1], pair[0]))), f'عداد {field} غير مطابق'
    assert stats.get('featured_count') == sum(1 for item in after_items if item.get('is_featured')), 'featured_count غير مطابق'
    assert stats.get('with_download_links') == sum(1 for item in after_items if int(item.get('download_links_count') or 0) > 0), 'with_download_links غير مطابق'

    validation = {
        'result': 'passed',
        'before_total': EXPECTED_BEFORE,
        'added_total': EXPECTED_ADDED,
        'after_total': EXPECTED_AFTER,
        'old_records_missing': len(missing_old_ids),
        'old_records_changed': len(changed_old_ids),
        'unexpected_new_records': len(added_ids - set(accepted_by_id)),
        'ids_duplicate_count': len(ids) - len(set(ids)),
        'main_public_items_match': after_items_text == public_items_text,
        'main_public_stats_match': stats_text == public_stats_text,
        'hero_counts': {key: stats.get(key) for key in ('qadaa_count', 'nizam_count', 'mohama_count')},
        'hero_sum': sum(int(stats.get(key, 0)) for key in ('qadaa_count', 'nizam_count', 'mohama_count')),
        'added_by_source': Counter(item['source'] for item in added),
        'added_by_category': Counter(item['category'] for item in added),
        'files_sha256': {
            'items.json': sha256_path(ITEMS_PATH),
            'client/public/items.json': sha256_path(PUBLIC_ITEMS_PATH),
            'stats.json': sha256_path(STATS_PATH),
            'client/public/stats.json': sha256_path(PUBLIC_STATS_PATH),
        },
    }
    VALIDATION_PATH.write_text(json.dumps(validation, ensure_ascii=False, indent=2, default=dict) + '\n', encoding='utf-8')
    print(json.dumps(validation, ensure_ascii=False, default=dict))


if __name__ == '__main__':
    main()
