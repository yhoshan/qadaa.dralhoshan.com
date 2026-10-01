#!/usr/bin/env python3
"""Validate public Drive link candidates without downloading source files."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
ITEMS_PATH = ROOT / 'items.json'
PUBLIC_ITEMS_PATH = ROOT / 'client/public/items.json'
STATS_PATH = ROOT / 'stats.json'
PUBLIC_STATS_PATH = ROOT / 'client/public/stats.json'
CANDIDATES_PATH = ROOT / 'drive_legal_links_2026-10-01_candidates.json'
ACCEPTED_PATH = ROOT / 'drive_legal_links_2026-10-01_accepted.json'
REPORT_PATH = ROOT / 'drive_legal_links_2026-10-01_precheck.json'

REQUIRED = {
    'id', 'title', 'link_drive', 'source', 'category', 'material_type',
    'file_type', 'download_links_count',
}


def normalize_title(value: str) -> str:
    value = unicodedata.normalize('NFKD', str(value or ''))
    value = ''.join(char for char in value if not unicodedata.combining(char))
    value = value.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ى', 'ي').replace('ة', 'ه').replace('ؤ', 'و').replace('ئ', 'ي')
    return re.sub(r'[^\w\d]+', '', value).lower()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def check_link(candidate: dict) -> dict:
    # stream=True and response.close() intentionally avoid downloading the document body.
    try:
        response = requests.get(candidate['link_drive'], allow_redirects=True, stream=True, timeout=25, headers={'User-Agent': 'Mozilla/5.0 (compatible; MakanezLinkAudit/1.0)'})
        status = response.status_code
        final_url = response.url
        content_type = response.headers.get('content-type', '')
        response.close()
        return {
            'id': candidate['id'],
            'url': candidate['link_drive'],
            'status': status,
            'final_url': final_url,
            'content_type': content_type,
            'available': status == 200 and 'drive.google.com' in final_url,
        }
    except Exception as exc:  # pragma: no cover - operational diagnostic
        return {
            'id': candidate['id'],
            'url': candidate['link_drive'],
            'status': None,
            'final_url': '',
            'content_type': '',
            'available': False,
            'error': str(exc),
        }


def main() -> None:
    main_text = ITEMS_PATH.read_text(encoding='utf-8')
    public_text = PUBLIC_ITEMS_PATH.read_text(encoding='utf-8')
    stats_text = STATS_PATH.read_text(encoding='utf-8')
    public_stats_text = PUBLIC_STATS_PATH.read_text(encoding='utf-8')
    if main_text != public_text:
        raise SystemExit('النسختان الرئيسية والمنشورة للمواد غير متطابقتين قبل الإضافة')
    if stats_text != public_stats_text:
        raise SystemExit('النسختان الرئيسية والمنشورة للإحصاءات غير متطابقتين قبل الإضافة')

    items = json.loads(main_text)
    candidates = json.loads(CANDIDATES_PATH.read_text(encoding='utf-8'))
    if not isinstance(items, list) or not isinstance(candidates, list):
        raise SystemExit('بنية بيانات غير متوقعة')
    if len(candidates) != 143:
        raise SystemExit(f'عدد المرشحين غير المتوقع: {len(candidates)}')

    existing_ids = {item.get('id') for item in items}
    existing_titles = {}
    existing_urls = {}
    for item in items:
        existing_titles.setdefault(normalize_title(item.get('title', '')), []).append(item)
        for field in ('link_telegram', 'link_drive', 'link_direct'):
            url = str(item.get(field, '')).rstrip('/')
            if url:
                existing_urls.setdefault(url, []).append(item)

    candidate_ids: set[str] = set()
    candidate_titles: set[str] = set()
    candidate_urls: set[str] = set()
    duplicates: list[dict] = []
    preflight_candidates: list[dict] = []
    for candidate in candidates:
        missing = sorted(field for field in REQUIRED if not candidate.get(field) and field != 'download_links_count')
        if missing:
            raise SystemExit(f"حقول مطلوبة مفقودة في {candidate.get('id')}: {', '.join(missing)}")
        if not candidate['id'].startswith('drive_'):
            raise SystemExit(f"بادئة معرّف غير مسموحة: {candidate['id']}")
        normalized_title = normalize_title(candidate['title'])
        url = candidate['link_drive'].rstrip('/')
        if not normalized_title:
            raise SystemExit(f"عنوان فارغ بعد التطبيع: {candidate['id']}")
        if not re.fullmatch(r'https://drive\.google\.com/file/d/[A-Za-z0-9_-]+/view', url):
            raise SystemExit(f"رابط Google Drive غير صالح: {url}")
        if candidate['id'] in existing_ids or candidate['id'] in candidate_ids:
            raise SystemExit(f"تكرار معرّف: {candidate['id']}")
        if normalized_title in candidate_titles:
            raise SystemExit(f"تكرار عنوان داخل المرشحين: {candidate['title']}")
        if url in candidate_urls:
            raise SystemExit(f"تكرار رابط داخل المرشحين: {url}")
        candidate_ids.add(candidate['id'])
        candidate_titles.add(normalized_title)
        candidate_urls.add(url)
        title_hits = existing_titles.get(normalized_title, [])
        url_hits = existing_urls.get(url, [])
        if title_hits or url_hits:
            duplicates.append({
                'candidate_id': candidate['id'],
                'candidate_title': candidate['title'],
                'candidate_url': url,
                'matching_existing_records': [
                    {'id': record.get('id'), 'title': record.get('title'), 'source': record.get('source')}
                    for record in {record.get('id'): record for record in title_hits + url_hits}.values()
                ],
                'reason': 'تطابق العنوان بعد التطبيع أو رابط العرض مع سجل قائم؛ لا يضاف مرة ثانية',
            })
        else:
            preflight_candidates.append(candidate)

    availability = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(check_link, candidate): candidate['id'] for candidate in preflight_candidates}
        for future in as_completed(futures):
            availability.append(future.result())
    availability.sort(key=lambda entry: entry['id'])
    unavailable_ids = {entry['id'] for entry in availability if not entry['available']}
    accepted = [candidate for candidate in preflight_candidates if candidate['id'] not in unavailable_ids]

    if len(accepted) != 137:
        raise SystemExit(f'عدد الإضافات القابلة للإدراج غير المتوقع: {len(accepted)}')
    if unavailable_ids:
        raise SystemExit(f'روابط غير متاحة: {sorted(unavailable_ids)}')

    ACCEPTED_PATH.write_text(json.dumps(accepted, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    report = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'mode': 'فحص روابط العرض العامة فقط؛ لم تُنزّل الملفات أو تُقرأ محتوياتها.',
        'before_total': len(items),
        'candidate_total': len(candidates),
        'existing_duplicates_excluded': len(duplicates),
        'unavailable_excluded': len(unavailable_ids),
        'accepted_total': len(accepted),
        'expected_after_total': len(items) + len(accepted),
        'main_items_sha256_before': sha256_text(main_text),
        'public_items_sha256_before': sha256_text(public_text),
        'stats_sha256_before': sha256_text(stats_text),
        'public_stats_sha256_before': sha256_text(public_stats_text),
        'duplicates': duplicates,
        'availability': availability,
        'accepted_ids': [candidate['id'] for candidate in accepted],
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'before_total': report['before_total'],
        'candidates': report['candidate_total'],
        'existing_duplicates_excluded': report['existing_duplicates_excluded'],
        'unavailable_excluded': report['unavailable_excluded'],
        'accepted_total': report['accepted_total'],
        'expected_after_total': report['expected_after_total'],
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
