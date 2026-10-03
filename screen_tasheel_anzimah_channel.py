#!/usr/bin/env python3
"""Conservative, reviewable screening for the public Telegram export of تسهيل الأنظمة.
Does not modify catalogue data.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path('/home/ubuntu/makanez-qadaa')
EXPORT = Path('/home/ubuntu/upload/pasted_file_K5SJyg_result.json')
ITEMS = ROOT / 'items.json'
RAW_OUT = ROOT / 'tasheel_anzimah_2026-10-03_raw_inventory.json'
CANDIDATES_OUT = ROOT / 'tasheel_anzimah_2026-10-03_candidates.json'
EXCLUDED_OUT = ROOT / 'tasheel_anzimah_2026-10-03_excluded.json'
PRECHECK_OUT = ROOT / 'tasheel_anzimah_2026-10-03_precheck.json'

# These are either expired one-off initiatives/drafts, general fiqh without a direct legal focus,
# or individual volumes fully covered by an existing 10-volume single catalogue record.
EXPLICIT_EXCLUSIONS = {
    4: 'مشروع لائحة مؤقت سبق اعتماد النسخة النهائية منه؛ لا يُفهرس كمصدر نظامي نافذ.',
    8: 'مبادرة تخفيض مروري مؤقتة انتهت في 2024؛ لا تصلح مرجعاً مستقراً.',
    41: 'إرشاد بروتوكولي للمخاطبات الرسمية، وليس مادة قضائية أو نظامية مرجعية.',
    70: 'فقه فرائض عام بلا اتصال قضائي أو نظامي خاص في عنوان الملف.',
    71: 'أصول فقه عام بلا اتصال قضائي أو نظامي خاص في عنوان الملف.',
    72: 'قواعد فقهية عامة بلا اتصال قضائي أو نظامي خاص في عنوان الملف.',
    74: 'نظريات فقهية عامة بلا اتصال قضائي أو نظامي خاص في عنوان الملف.',
}
# الوسيط في شرح القانون المدني: أجزاء مفردة مغطاة بسجل سابق بعنوان جميع الأجزاء 1–10.
EXPLICIT_EXCLUSIONS.update({i: 'جزء منفرد من «الوسيط في شرح القانون المدني»؛ يغطيه السجل القائم لجميع الأجزاء 1–10.' for i in range(87, 99)})

ARABIC_DIACRITICS = re.compile(r'[\u064B-\u065F\u0670\u06D6-\u06ED]')
CONTROL = re.compile(r'[\u200e\u200f\u202a-\u202e\u2066-\u2069]')


def clean_title(value: str) -> str:
    value = unicodedata.normalize('NFKC', value or '')
    value = CONTROL.sub('', value)
    value = re.sub(r'\.pdf$', '', value, flags=re.I)
    value = value.replace('_', ' ')
    value = re.sub(r'\s+', ' ', value).strip(' .-_–—')
    return value


def normalize(value: str) -> str:
    value = clean_title(value)
    value = ARABIC_DIACRITICS.sub('', value)
    value = value.translate(str.maketrans('أإآٱىةؤئ', 'اااايهوي'))
    value = re.sub(r'[^\w\s]', ' ', value, flags=re.UNICODE)
    value = re.sub(r'\s+', ' ', value).strip().lower()
    return value


def size_label(size: int | None) -> str:
    if not size:
        return ''
    return f'{size / (1024 * 1024):.1f} MB'


def classify(title: str) -> tuple[str, str]:
    # نوع المادة يصف طبيعة الملف أولاً: وجود لفظ «قضاء» في اسم تجميعي
    # لنظام أو لائحته لا يحوّل النظام إلى «أحكام».
    if re.search(r'^نظام\b|\bلائحة\b|الأنظمة الأساسية', title):
        if re.search(r'محاماة', title):
            return 'المحاماة والصياغة القانونية', 'نظام'
        if re.search(r'تحكيم|وساطة', title):
            return 'التحكيم والوساطة', 'نظام'
        if re.search(r'أحوال شخصية|تركات', title):
            return 'الأحوال الشخصية والتركات', 'نظام'
        if re.search(r'تجاري|شركة|شركات|إفلاس|منافسات|مشتريات|امتياز|استثمار|تمويل|مصرف|تأمين|أوراق تجارية|تستر|مساهمات', title):
            return 'القانون التجاري والاقتصادي', 'نظام'
        if re.search(r'إثبات|جزائي|مخدرات|تنفيذ|مرافعات|محكمة|تفتيش|جرائم|مرور|عقوبات|عدلية', title):
            return 'القضاء والإجراءات', 'نظام'
        return 'الأنظمة السعودية', 'نظام'
    if re.search(r'مدونة|تقريرات|سوابق|مبادئ|قرارات|أحكام', title):
        return 'القضاء والأحكام والإجراءات', 'أحكام'
    if re.search(r'محاماة|مذكرات|لوائح قانونية|صياغة قانونية|مرافعة', title):
        return 'المحاماة والصياغة القانونية', 'دليل إجرائي'
    if re.search(r'تحكيم|وساطة', title):
        return 'التحكيم والوساطة', 'نظام'
    if re.search(r'أحوال شخصية|تركات|فرائض', title):
        return 'الأحوال الشخصية والتركات', 'نظام'
    if re.search(r'تجاري|شركة|شركات|إفلاس|منافسات|مشتريات|امتياز|استثمار|تمويل|مصرف|تأمين|أوراق تجارية|تستر|مساهمات', title):
        return 'القانون التجاري والاقتصادي', 'نظام' if 'نظام' in title else 'بحث'
    if re.search(r'إثبات|جزائي|مخدرات|تنفيذ|مرافعات|محكمة|تفتيش|جرائم|مرور|عقوبات|عدلية', title):
        return 'القضاء والإجراءات', 'نظام' if 'نظام' in title else 'بحث'
    if re.search(r'شرح|تطبيقات|تسبيبات|تعليقات|دلالات|طرق|أسس|ضوابط|وجيز|إحاطة|خلاصة|دليل|مذكرة|فهرس', title):
        return 'الدراسات والمهارات القانونية', 'شرح'
    if re.search(r'نظام|لائحة|الأنظمة|تعميم', title):
        return 'الأنظمة السعودية', 'نظام'
    if re.search(r'حقوق المؤلف|ملكية فكرية|علامات|براءات|دوائر متكاملة|مؤشرات جغرافية|أصناف نباتية', title):
        return 'الملكية الفكرية', 'مادة قانونية'
    return 'الأنظمة السعودية', 'مادة قانونية'


def main() -> None:
    source_data = json.loads(EXPORT.read_text(encoding='utf8'))
    existing = json.loads(ITEMS.read_text(encoding='utf8'))
    existing_ids = {str(x.get('id', '')) for x in existing}
    existing_title_index: dict[str, list[dict]] = {}
    for item in existing:
        key = normalize(str(item.get('title', '')))
        if key:
            existing_title_index.setdefault(key, []).append(item)

    raw: list[dict] = []
    included: list[dict] = []
    excluded: list[dict] = []
    for msg in source_data.get('messages', []):
        if msg.get('type') != 'message' or msg.get('mime_type') != 'application/pdf' or not msg.get('file_name'):
            continue
        post_id = int(msg['id'])
        title = clean_title(str(msg['file_name']))
        item_id = f'muath_{post_id}'
        raw_record = {
            'post_id': post_id,
            'id': item_id,
            'title': title,
            'date': msg.get('date', ''),
            'file_name': msg.get('file_name', ''),
            'file_size_bytes': msg.get('file_size'),
            'telegram_url': f'https://t.me/muath_alyahya/{post_id}',
            'reply_to_message_id': msg.get('reply_to_message_id'),
        }
        raw.append(raw_record)
        if post_id in EXPLICIT_EXCLUSIONS:
            excluded.append({**raw_record, 'reason': EXPLICIT_EXCLUSIONS[post_id]})
            continue
        if item_id in existing_ids:
            excluded.append({**raw_record, 'reason': 'المعرّف موجود مسبقاً في المكنز؛ منع تكرار مطابق.'})
            continue
        exact_matches = existing_title_index.get(normalize(title), [])
        if exact_matches:
            excluded.append({
                **raw_record,
                'reason': 'عنوان مطابق بعد التطبيع لسجل قائم؛ منع تكرار مؤكد.',
                'matching_existing_ids': [x.get('id') for x in exact_matches],
                'matching_existing_titles': [x.get('title') for x in exact_matches],
            })
            continue
        category, material_type = classify(title)
        year = str(msg.get('date', ''))[:4] or ''
        included.append({
            'id': item_id,
            'title': title,
            'author': 'م. معاذ اليحيى',
            'investigator': '',
            'publisher': '',
            'year': year,
            'link_telegram': raw_record['telegram_url'],
            'link_drive': '',
            'link_direct': '',
            'source': 'تسهيل الأنظمة',
            'category': category,
            'material_type': material_type,
            'file_type': 'PDF',
            'file_size': size_label(msg.get('file_size')),
            'pages_count': '',
            'is_featured': False,
            'download_links_count': 1,
        })

    assert len(raw) == 275, f'expected 275 PDF files, got {len(raw)}'
    ids = [x['id'] for x in included]
    assert len(ids) == len(set(ids)), 'duplicate candidate IDs'
    assert not set(ids) & existing_ids, 'candidate IDs overlap existing IDs'
    assert not any(normalize(x['title']) in existing_title_index for x in included), 'exact title duplicate entered candidates'

    RAW_OUT.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    CANDIDATES_OUT.write_text(json.dumps(included, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    EXCLUDED_OUT.write_text(json.dumps(excluded, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    summary = {
        'source_export': str(EXPORT),
        'channel': source_data.get('name'),
        'channel_id': source_data.get('id'),
        'raw_pdf_records': len(raw),
        'accepted_candidates': len(included),
        'excluded_records': len(excluded),
        'excluded_by_reason': dict(Counter(x['reason'] for x in excluded)),
        'accepted_by_category': dict(Counter(x['category'] for x in included)),
        'accepted_by_material_type': dict(Counter(x['material_type'] for x in included)),
        'items_before_count': len(existing),
        'items_before_sha256': hashlib.sha256(ITEMS.read_bytes()).hexdigest(),
        'candidate_ids_sha256': hashlib.sha256('\n'.join(ids).encode()).hexdigest(),
        'checks': {
            'all_raw_files_are_pdf': len(raw) == 275,
            'candidate_ids_unique': len(ids) == len(set(ids)),
            'candidate_ids_absent_before_addition': not bool(set(ids) & existing_ids),
            'candidate_titles_not_exact_duplicates_after_normalization': not any(normalize(x['title']) in existing_title_index for x in included),
        },
    }
    PRECHECK_OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
