import json
from datetime import date
from pathlib import Path

PROJECT = Path('/home/ubuntu/makanez-qadaa')
ITEMS_PATH = PROJECT / 'items.json'
PUBLIC_ITEMS_PATH = PROJECT / 'client/public/items.json'
STATS_PATH = PROJECT / 'client/public/stats.json'

SOURCE = 'موقع د. عبدالعزيز الدغيثر (شبكة الألوكة)'
AUTHOR = 'د. عبدالعزيز بن سعد الدغيثر'

NEW_ITEMS = [
    {
        'id': 'doghaither_0050',
        'title': 'القضاء الجماعي والقضاء الفردي: دراسة فقهية قانونية مقارنة',
        'author': AUTHOR,
        'investigator': '',
        'publisher': 'شبكة الألوكة',
        'year': '2017',
        'link_telegram': '',
        'link_drive': '',
        'link_direct': 'https://www.alukah.net/web/doghaither/0/122907/',
        'source': SOURCE,
        'category': 'القضاء الشرعي',
        'material_type': 'بحث',
        'file_type': 'PDF',
        'file_size': '',
        'pages_count': '64',
        'is_featured': False,
        'download_links_count': 1,
    },
    {
        'id': 'doghaither_0062',
        'title': 'تنظيم المنافسة في المملكة العربية السعودية',
        'author': AUTHOR,
        'investigator': '',
        'publisher': 'شبكة الألوكة',
        'year': '2017',
        'link_telegram': '',
        'link_drive': '',
        'link_direct': 'https://www.alukah.net/web/doghaither/0/123228/',
        'source': SOURCE,
        'category': 'الأنظمة والتشريعات',
        'material_type': 'كتاب',
        'file_type': 'PDF',
        'file_size': '',
        'pages_count': '',
        'is_featured': False,
        'download_links_count': 1,
    },
    {
        'id': 'doghaither_0063',
        'title': 'أسس النظر في التركزات في ضوء نظام المنافسة',
        'author': AUTHOR,
        'investigator': '',
        'publisher': 'شبكة الألوكة',
        'year': '2017',
        'link_telegram': '',
        'link_drive': '',
        'link_direct': 'https://www.alukah.net/web/doghaither/0/123294/',
        'source': SOURCE,
        'category': 'الأنظمة والتشريعات',
        'material_type': 'بحث',
        'file_type': 'PDF',
        'file_size': '',
        'pages_count': '',
        'is_featured': False,
        'download_links_count': 1,
    },
    {
        'id': 'doghaither_0917',
        'title': 'زكاة المكاتب الاستشارية (الهندسية والمحاسبية والمحاماة)',
        'author': AUTHOR,
        'investigator': '',
        'publisher': 'شبكة الألوكة',
        'year': '2022',
        'link_telegram': '',
        'link_drive': '',
        'link_direct': 'https://www.alukah.net/web/doghaither/12245/154224/%D8%B2%D9%83%D8%A7%D8%A9-%D8%A7%D9%84%D9%85%D9%83%D8%A7%D8%AA%D8%A8-%D8%A7%D9%84%D8%A7%D8%B3%D8%AA%D8%B4%D8%A7%D8%B1%D9%8A%D8%A9-%D8%A7%D9%84%D9%87%D9%86%D8%AF%D8%B3%D9%8A%D8%A9-%D9%88%D8%A7%D9%84%D9%85%D8%AD%D8%A7%D8%B3%D8%A8%D9%8A%D8%A9-%D9%88%D8%A7%D9%84%D9%85%D8%AD%D8%A7%D9%85%D8%A7%D8%A9/',
        'source': SOURCE,
        'category': 'المحاماة والمرافعات',
        'material_type': 'مقال',
        'file_type': 'رابط',
        'file_size': '',
        'pages_count': '',
        'is_featured': False,
        'download_links_count': 1,
    },
]

with ITEMS_PATH.open(encoding='utf-8') as file:
    items = json.load(file)

known_ids = {item.get('id') for item in items}
known_links = {item.get('link_direct') for item in items if item.get('link_direct')}
accepted = [item for item in NEW_ITEMS if item['id'] not in known_ids and item['link_direct'] not in known_links]

items.extend(accepted)
with ITEMS_PATH.open('w', encoding='utf-8') as file:
    json.dump(items, file, ensure_ascii=False, indent=2)
with PUBLIC_ITEMS_PATH.open('w', encoding='utf-8') as file:
    json.dump(items, file, ensure_ascii=False, indent=2)

with STATS_PATH.open(encoding='utf-8') as file:
    stats = json.load(file)

stats['total_items'] = len(items)
stats['qadaa_count'] = int(stats.get('qadaa_count', 0)) + sum(item['category'] == 'القضاء الشرعي' for item in accepted)
stats['nizam_count'] = int(stats.get('nizam_count', 0)) + sum(item['category'] == 'الأنظمة والتشريعات' for item in accepted)
stats['mohama_count'] = int(stats.get('mohama_count', 0)) + sum(item['category'] == 'المحاماة والمرافعات' for item in accepted)
stats['research_count'] = int(stats.get('research_count', 0)) + sum(item['material_type'] == 'بحث' for item in accepted)
stats['last_updated'] = date.today().isoformat()

with STATS_PATH.open('w', encoding='utf-8') as file:
    json.dump(stats, file, ensure_ascii=False, indent=2)

print(json.dumps({
    'accepted_count': len(accepted),
    'total_items': stats['total_items'],
    'qadaa_count': stats['qadaa_count'],
    'nizam_count': stats['nizam_count'],
    'mohama_count': stats['mohama_count'],
    'research_count': stats['research_count'],
}, ensure_ascii=False, indent=2))
