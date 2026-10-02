#!/usr/bin/env python3
"""Create a conservative, read-only inventory from the Jabar Telegram export."""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPORT = Path('/home/ubuntu/upload/pasted_file_8Dk768_result.json')
OUT_JSON = ROOT / 'jabar_channel_2026-10-02_screening.json'
OUT_CSV = ROOT / 'jabar_channel_2026-10-02_screening.csv'
SUMMARY = ROOT / 'jabar_channel_2026-10-02_screening_summary.json'

FILE_EXTENSIONS = {'.pdf': 'PDF', '.doc': 'Word', '.docx': 'Word', '.xls': 'Excel', '.xlsx': 'Excel', '.ppt': 'PowerPoint', '.pptx': 'PowerPoint'}
LEGAL_TERMS = (
    'نظام', 'نظامي', 'قانون', 'قضائ', 'محكم', 'محام', 'لائح', 'اعتراض',
    'دعوى', 'مرافع', 'تنفيذ', 'عقد', 'التزام', 'إثبات', 'اثبات', 'تجاري',
    'عمال', 'الأحوال الشخصية', 'احوال شخصية', 'جزائ', 'جنائ', 'مخدر', 'حكم',
    'أحكام', 'قرار', 'مبادئ', 'تسبيب', 'مدني', 'عقار', 'ضريب', 'جمرك',
    'إفلاس', 'افلاس', 'ناجز', 'توثيق', 'ملكية', 'تأمين', 'شركة', 'استشارة',
    'تحكيم', 'شكوى', 'شكوى', 'تظلم', 'خطاب جهة حكومية', 'رقابة', 'جرائم',
    'جريمة', 'لجنة', 'ديوان المظالم', 'المدعي', 'المحكمة العليا', 'تمييز',
)
EXCLUSION_TERMS = (
    'لا أسمح بنشر', 'شراء الكتاب', 'النسخة الورقية', 'طلبات النسخة',
    'فرص العمل', 'التقدم على وظائف', 'سيرة ذاتية', 'مقابلات وظيفية',
    'بوت سيراس', 'كود في تطبيق', 'gemini', 'عميل متظلم', 'للمتابعة',
)
URL_RE = re.compile(r'https?://[^\s\]\)"<>]+', re.I)
ARABIC_DIACRITICS = re.compile(r'[\u064B-\u065F\u0670]')
TATWEEL = re.compile(r'ـ')
REMOVE_MARKS = re.compile(r'[^\w\s]', re.UNICODE)


def text_value(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        chunks: list[str] = []
        for part in value:
            if isinstance(part, str):
                chunks.append(part)
            elif isinstance(part, dict):
                chunks.append(str(part.get('text') or part.get('href') or ''))
        return ''.join(chunks)
    return ''


def clean_title(value: str) -> str:
    value = value.replace('\u200e', '').replace('\u200f', '').replace('\u2068', '').replace('\u2069', '')
    value = re.sub(r'^.*?⁨', '', value).replace('⁩', '')
    value = re.sub(r'\.(pdf|docx?|xlsx?|pptx?)$', '', value, flags=re.I)
    value = re.sub(r'[_\-]+', ' ', value)
    value = re.sub(r'\s+', ' ', value).strip(' .،؛:')
    return value


def norm(value: str) -> str:
    value = unicodedata.normalize('NFKC', value).lower()
    value = ARABIC_DIACRITICS.sub('', value)
    value = TATWEEL.sub('', value)
    value = re.sub('[إأآٱ]', 'ا', value)
    value = value.replace('ى', 'ي').replace('ة', 'ه')
    value = REMOVE_MARKS.sub(' ', value)
    return re.sub(r'\s+', ' ', value).strip()


def entity_links(message: dict, text: str) -> list[str]:
    links: list[str] = []
    for entity in message.get('text_entities') or []:
        if not isinstance(entity, dict):
            continue
        if entity.get('type') in {'link', 'text_link'}:
            link = str(entity.get('href') or entity.get('text') or '').strip()
            if link:
                links.append(link)
    links.extend(URL_RE.findall(text))
    result: list[str] = []
    seen: set[str] = set()
    for link in links:
        link = link.rstrip('.,،؛:)]}')
        if link and link not in seen:
            seen.add(link)
            result.append(link)
    return result


def title_from_text(text: str) -> str:
    text = text.replace('\n', ' ')
    text = re.sub(r'https?://\S+', ' ', text)
    text = re.sub(r'[📌📍📝⚖️📚🗂️🔗‼️📃🧳✍🏼✔️💡💻📬🏛️👮🏻‍♂️👷🏻‍♂️📘📖🗾]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    # Prefer first substantive line or label.
    chunks = re.split(r'(?:رابط التحميل|لتحميل الملف|رابط الملف|رابط:|التحميل:|للتفاصيل|إعداد:|اعداد:|يحتوي|يتضمن|وهو عبارة)', text, maxsplit=1, flags=re.I)
    return clean_title(chunks[0])[:240]


def category_for(title: str) -> str:
    t = norm(title)
    if any(term in t for term in ('محام', 'صياغ', 'لائح', 'مذكر', 'عقد', 'استشار')):
        return 'المحاماة والتحكيم'
    if any(term in t for term in ('محكم', 'قضائ', 'حكم', 'دعوي', 'مرافع', 'تنفيذ', 'اثبات', 'تسبيب', 'قرار', 'مبادي')):
        return 'المحاكم والمرافعات'
    if any(term in t for term in ('مخدر', 'جنائ', 'جزائ', 'جريم')):
        return 'القضايا الجنائية'
    if any(term in t for term in ('احوال', 'اسره', 'حضانه', 'طلاق', 'نفقه')):
        return 'الأحوال الشخصية'
    return 'الأنظمة والتشريعات'


def material_type_for(title: str, is_folder: bool) -> str:
    t = norm(title)
    if is_folder:
        return 'رابط مرجعي'
    if any(term in t for term in ('نموذج', 'مذكر', 'لائح', 'خطاب', 'شكوي', 'صحيفه')):
        return 'مذكرة'
    if any(term in t for term in ('نظام', 'لائحه', 'تعميم', 'قرار')):
        return 'نظام'
    if any(term in t for term in ('دليل', 'حقيبه')):
        return 'دليل'
    if any(term in t for term in ('حكم', 'مبادي', 'تسبيب', 'سوابق', 'تقارير محكمه')):
        return 'حكم قضائي'
    return 'كتاب'


def title_is_legal(title: str, text: str) -> bool:
    haystack = norm(f'{title} {text}')
    return any(norm(term) in haystack for term in LEGAL_TERMS)


def main() -> None:
    payload = json.loads(EXPORT.read_text(encoding='utf-8'))
    channel = payload.get('name') or 'جبار'
    messages = payload.get('messages') or []
    items = json.loads((ROOT / 'items.json').read_text(encoding='utf-8'))
    existing_ids = {str(item.get('id')) for item in items}
    existing_titles = {norm(str(item.get('title') or '')) for item in items}
    existing_links = {str(item.get(field) or '').split('?')[0] for item in items for field in ('link_drive', 'link_direct', 'link_telegram') if item.get(field)}

    records: list[dict] = []
    for message in messages:
        message_id = message.get('id')
        if not isinstance(message_id, int):
            continue
        text = text_value(message.get('text'))
        file_name = str(message.get('file_name') or '')
        suffix = Path(file_name).suffix.lower()
        links = entity_links(message, text)
        is_file = suffix in FILE_EXTENSIONS
        drive_links = [link for link in links if 'drive.google.com/' in link or 'docs.google.com/' in link]
        is_folder = any('/folders/' in link or '/folder/' in link for link in drive_links)

        kind = None
        title = ''
        link = ''
        file_type = ''
        if is_file:
            kind = 'channel_file'
            title = clean_title(file_name)
            link = f'https://t.me/jabaraiar/{message_id}'
            file_type = FILE_EXTENSIONS[suffix]
        elif drive_links:
            kind = 'drive_reference'
            title = title_from_text(text)
            link = drive_links[0]
            file_type = 'رابط'
        else:
            continue

        exclusion_reason = ''
        lower_text = norm(f'{title} {text}')
        if any(norm(term) in lower_text for term in EXCLUSION_TERMS):
            exclusion_reason = 'إعلان أو مادة مدفوعة أو محتوى وظيفي/توليدي غير مرجعي'
        elif not title or len(norm(title)) < 4:
            exclusion_reason = 'عنوان غير كافٍ للفهرسة'
        elif not title_is_legal(title, text):
            exclusion_reason = 'لا تظهر صلة قانونية أو قضائية واضحة'

        canonical_link = link.split('?')[0]
        row = {
            'channel': channel,
            'message_id': message_id,
            'date': message.get('date') or '',
            'kind': kind,
            'title': title,
            'author': '',
            'source': 'قناة جبار',
            'category': category_for(title),
            'material_type': material_type_for(title, is_folder),
            'file_type': file_type,
            'file_size': str(message.get('file_size') or ''),
            'pages_count': '',
            'official_or_public_link': link,
            'existing_title_match': norm(title) in existing_titles,
            'existing_link_match': canonical_link in existing_links,
            'proposed_id': f'jabar_{message_id}',
            'candidate_status': 'exclude' if exclusion_reason else 'review',
            'reason': exclusion_reason or 'يتطلب فحص التكرار والرابط قبل الإدخال',
            'excerpt': text[:1200],
        }
        if row['proposed_id'] in existing_ids:
            row['candidate_status'] = 'exclude'
            row['reason'] = 'معرف القناة مستخدم مسبقاً'
        elif row['existing_title_match']:
            row['candidate_status'] = 'exclude'
            row['reason'] = 'عنوان مطابق لسجل قائم بعد التطبيع'
        elif row['existing_link_match']:
            row['candidate_status'] = 'exclude'
            row['reason'] = 'رابط مطابق لسجل قائم'
        records.append(row)

    OUT_JSON.write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    columns = [key for key in records[0].keys()] if records else []
    with OUT_CSV.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(records)
    summary = {
        'channel': channel,
        'messages_total': len(messages),
        'records_screened': len(records),
        'by_kind': Counter(row['kind'] for row in records),
        'by_status': Counter(row['candidate_status'] for row in records),
        'excluded_reasons': Counter(row['reason'] for row in records if row['candidate_status'] == 'exclude'),
        'review_candidates': [row['message_id'] for row in records if row['candidate_status'] == 'review'],
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=dict) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, default=dict))


if __name__ == '__main__':
    main()
