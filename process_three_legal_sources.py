import json
import re
import unicodedata
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

PROJECT = Path('/home/ubuntu/makanez-qadaa')
INPUT = Path('/home/ubuntu/upload/pasted_file_JTyNI0_deepseek_json_20260818_499856.json')
ITEMS_PATH = PROJECT / 'items.json'
PUBLIC_ITEMS_PATH = PROJECT / 'client/public/items.json'
STATS_PATH = PROJECT / 'client/public/stats.json'
REPORT_PATH = PROJECT / 'three_legal_sources_report.json'

SOURCE_NAME = 'المكتبة القانونية — موقع المحامي نواف بن عواض الحربي'


def normalize(value: str) -> str:
    value = unicodedata.normalize('NFKC', value or '')
    value = re.sub(r'[أإآٱ]', 'ا', value)
    value = value.replace('ى', 'ي').replace('ة', 'ه')
    value = re.sub(r'[\W_]+', ' ', value, flags=re.UNICODE)
    return re.sub(r'\s+', ' ', value).strip().lower()


def classify(category_name: str, title: str) -> tuple[str, str]:
    if 'العمال' in category_name:
        category = 'القضاء العمالي'
    elif 'التجاري' in category_name:
        category = 'القضاء التجاري'
    elif 'الإداري' in category_name:
        category = 'القضاء الإداري'
    elif 'الأحوال الشخصية' in category_name:
        category = 'الأحوال الشخصية'
    elif 'الأنظمة' in category_name:
        category = 'الأنظمة والتشريعات'
    elif 'تنفيذ' in category_name or 'أحكام' in category_name or 'تعاميم' in category_name or 'نماذج' in category_name or 'شبه القضائية' in category_name:
        category = 'المحاكم والمرافعات'
    else:
        category = 'القضاء الشرعي'

    if title.startswith('نظام ') or title.startswith('اللائحة'):
        material_type = 'نظام'
    elif title.startswith('تعميم') or title.startswith('قرار') or title.startswith('مرسوم'):
        material_type = 'قرار'
    elif any(term in title for term in ('حقيبة تدريبية', 'مذكرة', 'دليل', 'قوالب', 'نماذج', 'مدونة', 'مجموعة الأحكام', 'مجموعة المبادئ')):
        material_type = 'مادة قانونية'
    else:
        material_type = 'كتاب'
    return category, material_type


def stats_bucket(category: str) -> str:
    if any(term in category for term in ('قضاء', 'محاكم', 'إجراءات', 'أحوال')):
        return 'qadaa_count'
    if 'محاماة' in category:
        return 'mohama_count'
    return 'nizam_count'


with INPUT.open(encoding='utf-8') as file:
    input_data = json.load(file)
with ITEMS_PATH.open(encoding='utf-8') as file:
    items = json.load(file)
with STATS_PATH.open(encoding='utf-8') as file:
    stats = json.load(file)

existing_titles = [normalize(item.get('title', '')) for item in items if item.get('title')]
existing_title_set = set(existing_titles)
existing_by_prefix: dict[str, list[str]] = {}
for title in existing_titles:
    existing_by_prefix.setdefault(title[:18], []).append(title)

nawaf = next(source for source in input_data['sources'] if source['id'] == 'source_1_nawaf')
accepted = []
duplicates = []
skipped_indexes = []

for category in nawaf['categories']:
    category_name = category['name']
    if category_name == 'الفهارس':
        skipped_indexes.extend(book['title'] for book in category['books'])
        continue
    for book in category['books']:
        title = re.sub(r'\s+', ' ', book.get('title', '')).strip()
        if not title:
            continue
        normalized_title = normalize(title)
        similar_titles = existing_by_prefix.get(normalized_title[:18], [])
        duplicate = normalized_title in existing_title_set or any(
            normalized_title in previous or previous in normalized_title or SequenceMatcher(None, normalized_title, previous).ratio() >= 0.94
            for previous in similar_titles
        )
        if duplicate:
            duplicates.append({'title': title, 'category': category_name})
            continue

        item_category, material_type = classify(category_name, title)
        item = {
            'id': f'nawaf_{len(accepted) + 1:03d}',
            'title': title,
            'author': book.get('author') or '',
            'investigator': '',
            'publisher': 'موقع المحامي نواف بن عواض الحربي',
            'year': '',
            'link_telegram': '',
            'link_drive': '',
            'link_direct': category['page_url'],
            'source': SOURCE_NAME,
            'category': item_category,
            'material_type': material_type,
            'file_type': 'رابط',
            'file_size': '',
            'pages_count': '',
            'is_featured': False,
            'download_links_count': 1,
        }
        accepted.append(item)
        existing_titles.append(normalized_title)
        existing_title_set.add(normalized_title)
        existing_by_prefix.setdefault(normalized_title[:18], []).append(normalized_title)

items.extend(accepted)
for item in accepted:
    bucket = stats_bucket(item['category'])
    stats[bucket] = int(stats.get(bucket, 0)) + 1
stats['total_items'] = len(items)
stats['last_updated'] = date.today().isoformat()

for path, data in ((ITEMS_PATH, items), (PUBLIC_ITEMS_PATH, items), (STATS_PATH, stats)):
    with path.open('w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

report = {
    'added_source': SOURCE_NAME,
    'added_count': len(accepted),
    'duplicates_count': len(duplicates),
    'skipped_indexes_count': len(skipped_indexes),
    'skipped_existing_source': 'منصة نظامي للأنظمة السعودية (20 عنواناً في الملف؛ المصدر مضاف سابقاً)',
    'skipped_paid_source': 'الجمعية العلمية القضائية (قضاء) — 127 عنواناً معروضة بأسعار؛ لم تضف للمكنز احتراماً لحقوق النشر',
    'updated_stats': stats,
    'added_items': accepted,
    'duplicates': duplicates,
}
with REPORT_PATH.open('w', encoding='utf-8') as file:
    json.dump(report, file, ensure_ascii=False, indent=2)

print(json.dumps({
    'added_count': len(accepted),
    'duplicates_count': len(duplicates),
    'skipped_indexes_count': len(skipped_indexes),
    'updated_stats': stats,
}, ensure_ascii=False, indent=2))
