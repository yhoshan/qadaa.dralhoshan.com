import json
import re
import unicodedata
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse

PROJECT = Path('/home/ubuntu/makanez-qadaa')
INPUT = Path('/home/ubuntu/upload/pasted_file_R1NusN_deepseek_json_20260818_75bedd.json')
ITEMS_PATH = PROJECT / 'items.json'
PUBLIC_ITEMS_PATH = PROJECT / 'client/public/items.json'
STATS_PATH = PROJECT / 'client/public/stats.json'
REPORT_PATH = PROJECT / 'nezams_source_report.json'

SOURCE = 'منصة نظامي للأنظمة السعودية (nezams.com)'

def normalize(value):
    value = unicodedata.normalize('NFKC', value or '')
    value = re.sub(r'[أإآٱ]', 'ا', value)
    value = value.replace('ى', 'ي').replace('ة', 'ه')
    value = re.sub(r'[^\w\s]', ' ', value, flags=re.UNICODE)
    return re.sub(r'\s+', ' ', value).strip().lower()

def canonical_url(value):
    parsed = urlparse(value)
    return f'{parsed.scheme.lower()}://{parsed.netloc.lower()}{parsed.path.rstrip("/")}'

def classify(category_name, title):
    title_text = title.lower()
    if 'المحاماة' in title_text:
        return 'المحاماة والمرافعات', 'نظام'
    if title in {'نظام القضاء'}:
        return 'القضاء الشرعي', 'نظام'
    if any(term in title_text for term in ['المرافعات', 'الإثبات', 'التنفيذ', 'المحاكم', 'التوثيق', 'التحكيم']):
        return 'المحاكم والمرافعات', 'نظام'
    if 'الجزائي' in category_name or 'جزائي' in title_text or 'التزوير' in title_text or 'المبل' in title_text:
        return 'الأنظمة الجزائية', 'نظام'
    if 'تحديثات' in category_name:
        return 'الأنظمة والتشريعات', 'قرار'
    return 'الأنظمة والتشريعات', 'نظام'

def stats_bucket(category):
    if category in {'القضاء الشرعي', 'المحاكم والمرافعات'}:
        return 'qadaa_count'
    if category == 'المحاماة والمرافعات':
        return 'mohama_count'
    return 'nizam_count'

with INPUT.open(encoding='utf-8') as file:
    source_data = json.load(file)
with ITEMS_PATH.open(encoding='utf-8') as file:
    items = json.load(file)
with STATS_PATH.open(encoding='utf-8') as file:
    stats = json.load(file)

existing_titles = [normalize(item.get('title', '')) for item in items if item.get('title')]
existing_links = {canonical_url(item.get('link_direct', '')) for item in items if item.get('link_direct')}
new_items = []
duplicates = []

for category in source_data.get('categories', []):
    for entry in category.get('items', []):
        title = re.sub(r'\s+', ' ', entry.get('title', '')).strip()
        link = entry.get('url', '').strip()
        if not title or not link:
            continue
        title_normalized = normalize(title)
        link_canonical = canonical_url(link)
        closest = max((SequenceMatcher(None, title_normalized, existing).ratio() for existing in existing_titles), default=0)
        if link_canonical in existing_links or closest >= 0.93:
            duplicates.append({
                'title': title,
                'url': link,
                'closest_title_score': round(closest, 3),
                'reason': 'رابط موجود أو عنوان مكرر/شديد التشابه',
            })
            continue
        item_category, material_type = classify(category['name'], title)
        item_id = f"nezams_{len(new_items) + 1:03d}"
        new_item = {
            'id': item_id,
            'title': title,
            'author': '',
            'investigator': '',
            'publisher': 'منصة نظامي للأنظمة السعودية',
            'year': '',
            'link_telegram': '',
            'link_drive': '',
            'link_direct': link,
            'source': SOURCE,
            'category': item_category,
            'material_type': material_type,
            'file_type': 'رابط',
            'file_size': '',
            'pages_count': '',
            'is_featured': False,
            'download_links_count': 1,
        }
        new_items.append(new_item)
        existing_titles.append(title_normalized)
        existing_links.add(link_canonical)

items.extend(new_items)
with ITEMS_PATH.open('w', encoding='utf-8') as file:
    json.dump(items, file, ensure_ascii=False, indent=2)
with PUBLIC_ITEMS_PATH.open('w', encoding='utf-8') as file:
    json.dump(items, file, ensure_ascii=False, indent=2)

for item in new_items:
    stats[stats_bucket(item['category'])] = int(stats.get(stats_bucket(item['category']), 0)) + 1
stats['total_items'] = len(items)
stats['last_updated'] = date.today().isoformat()
with STATS_PATH.open('w', encoding='utf-8') as file:
    json.dump(stats, file, ensure_ascii=False, indent=2)

report = {
    'source': SOURCE,
    'source_url': source_data.get('source', ''),
    'input_count': sum(len(category.get('items', [])) for category in source_data.get('categories', [])),
    'added_count': len(new_items),
    'duplicates_count': len(duplicates),
    'added_items': new_items,
    'duplicates': duplicates,
    'updated_stats': stats,
}
with REPORT_PATH.open('w', encoding='utf-8') as file:
    json.dump(report, file, ensure_ascii=False, indent=2)

print(json.dumps({
    'input_count': report['input_count'],
    'added_count': report['added_count'],
    'duplicates_count': report['duplicates_count'],
    'stats': report['updated_stats'],
}, ensure_ascii=False, indent=2))
