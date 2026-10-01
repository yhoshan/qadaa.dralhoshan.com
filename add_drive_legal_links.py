#!/usr/bin/env python3
"""Add validated public Drive title-and-link records without downloading files."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ITEMS_PATH = ROOT / 'items.json'
PUBLIC_ITEMS_PATH = ROOT / 'client/public/items.json'
STATS_PATH = ROOT / 'stats.json'
PUBLIC_STATS_PATH = ROOT / 'client/public/stats.json'
CACHE_PATH = ROOT / 'client/src/hooks/useItems.ts'
ACCEPTED_PATH = ROOT / 'drive_legal_links_2026-10-01_accepted.json'
PRECHECK_PATH = ROOT / 'drive_legal_links_2026-10-01_precheck.json'
EXECUTION_PATH = ROOT / 'drive_legal_links_2026-10-01_execution.json'

EXPECTED_BEFORE_TOTAL = 17481
EXPECTED_ADD_TOTAL = 137
CURRENT_CACHE_TOKEN = 'qadaa-eight-id-targeted-removal-2026-10-01'
NEXT_CACHE_TOKEN = 'qadaa-drive-legal-links-2026-10-01'


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def count_by(items: list[dict], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = str(item.get(field) or '')
        if value:
            counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items(), key=lambda pair: (-pair[1], pair[0])))


def public_record(candidate: dict) -> dict:
    return {key: value for key, value in candidate.items() if not key.startswith('_')}


def main() -> None:
    main_text = ITEMS_PATH.read_text(encoding='utf-8')
    public_text = PUBLIC_ITEMS_PATH.read_text(encoding='utf-8')
    stats_text = STATS_PATH.read_text(encoding='utf-8')
    public_stats_text = PUBLIC_STATS_PATH.read_text(encoding='utf-8')
    cache = CACHE_PATH.read_text(encoding='utf-8')
    if main_text != public_text:
        raise SystemExit('النسختان الرئيسية والمنشورة للمواد غير متطابقتين قبل الإضافة')
    if stats_text != public_stats_text:
        raise SystemExit('النسختان الرئيسية والمنشورة للإحصاءات غير متطابقتين قبل الإضافة')
    if CURRENT_CACHE_TOKEN not in cache:
        raise SystemExit('تعذر العثور على معلمة كسر الكاش الحالية')

    items = json.loads(main_text)
    stats = json.loads(stats_text)
    accepted = json.loads(ACCEPTED_PATH.read_text(encoding='utf-8'))
    precheck = json.loads(PRECHECK_PATH.read_text(encoding='utf-8'))
    if not isinstance(items, list) or not isinstance(accepted, list):
        raise SystemExit('بنية البيانات غير متوقعة')
    if len(items) != EXPECTED_BEFORE_TOTAL:
        raise SystemExit(f'إجمالي سابق غير متوقع: {len(items)}')
    if len(accepted) != EXPECTED_ADD_TOTAL or precheck.get('accepted_total') != EXPECTED_ADD_TOTAL:
        raise SystemExit(f'عدد الإضافات المعتمد غير متوقع: {len(accepted)}')

    existing_ids = {item.get('id') for item in items}
    existing_urls = {
        str(item.get(field) or '').rstrip('/')
        for item in items
        for field in ('link_telegram', 'link_drive', 'link_direct')
        if item.get(field)
    }
    candidate_ids: set[str] = set()
    candidate_urls: set[str] = set()
    additions: list[dict] = []
    for raw_candidate in accepted:
        candidate = public_record(raw_candidate)
        item_id = candidate.get('id', '')
        url = str(candidate.get('link_drive', '')).rstrip('/')
        if not item_id.startswith('drive_'):
            raise SystemExit(f'معرّف غير مسموح: {item_id}')
        if not candidate.get('title') or not url:
            raise SystemExit(f'عنوان أو رابط مفقود: {item_id}')
        if item_id in existing_ids or item_id in candidate_ids:
            raise SystemExit(f'تكرار معرّف: {item_id}')
        if url in existing_urls or url in candidate_urls:
            raise SystemExit(f'تكرار رابط: {url}')
        if candidate.get('link_telegram') or candidate.get('link_direct'):
            raise SystemExit(f'الإضافة يجب أن تحمل رابط Drive فقط: {item_id}')
        if int(candidate.get('download_links_count', 0)) != 1:
            raise SystemExit(f'عدد روابط الإضافة غير صحيح: {item_id}')
        candidate_ids.add(item_id)
        candidate_urls.add(url)
        additions.append(candidate)

    updated_items = [*items, *additions]
    if len(updated_items) != EXPECTED_BEFORE_TOTAL + EXPECTED_ADD_TOTAL:
        raise SystemExit('إجمالي لاحق غير متوقع')
    updated_stats = {
        **stats,
        'total': len(updated_items),
        'total_items': len(updated_items),
        'categories': count_by(updated_items, 'category'),
        'sources': count_by(updated_items, 'source'),
        'material_types': count_by(updated_items, 'material_type'),
        'file_types': count_by(updated_items, 'file_type'),
        'featured_count': sum(1 for item in updated_items if item.get('is_featured')),
        'with_download_links': sum(1 for item in updated_items if int(item.get('download_links_count') or 0) > 0),
    }
    updated_cache = cache.replace(CURRENT_CACHE_TOKEN, NEXT_CACHE_TOKEN)

    ITEMS_PATH.write_text(json.dumps(updated_items, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    PUBLIC_ITEMS_PATH.write_text(json.dumps(updated_items, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    STATS_PATH.write_text(json.dumps(updated_stats, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    PUBLIC_STATS_PATH.write_text(json.dumps(updated_stats, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    CACHE_PATH.write_text(updated_cache, encoding='utf-8')

    execution = {
        'executed_at': datetime.now(timezone.utc).isoformat(),
        'operation': 'إضافة عناوين وروابط عامة من Google Drive فقط دون تنزيل الملفات',
        'before_total': len(items),
        'added_total': len(additions),
        'after_total': len(updated_items),
        'cache_buster': NEXT_CACHE_TOKEN,
        'source_counts': count_by(additions, 'source'),
        'category_counts': count_by(additions, 'category'),
        'ids': [item['id'] for item in additions],
        'main_items_sha256_before': sha256(main_text),
        'main_items_sha256_after': sha256(ITEMS_PATH.read_text(encoding='utf-8')),
        'notes': [
            'لم تُنزّل ملفات Drive؛ أضيفت العناوين وروابط العرض العامة فقط.',
            'استُبعدت العناوين الستة الموجودة سابقاً بحسب تقرير الفحص المسبق.',
        ],
    }
    EXECUTION_PATH.write_text(json.dumps(execution, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'before_total': execution['before_total'],
        'added_total': execution['added_total'],
        'after_total': execution['after_total'],
        'cache_buster': execution['cache_buster'],
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
