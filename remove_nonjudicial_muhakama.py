import json
from datetime import date
from pathlib import Path

PROJECT = Path('/home/ubuntu/makanez-qadaa')
ITEMS_PATH = PROJECT / 'items.json'
PUBLIC_ITEMS_PATH = PROJECT / 'client/public/items.json'
STATS_PATH = PROJECT / 'client/public/stats.json'
REPORT_PATH = PROJECT / 'muhakama_removal_report.json'

# عناوين أدبية أو نقدية أو تاريخية غير متعلقة بالمحاكمات القضائية.
REMOVALS = {
    'qadaa_1076': 'محاكمة عقدية بين شخصيات؛ ليست إجراءً قضائياً',
    'qadaa_1374': 'مقارنة تفسيرية بين المفسرين',
    'qadaa_2143': 'محاكمة نقدية بين العيني وابن حجر',
    'qadaa_2258': 'محاكمة حديثية بين الغماري وابن عاشور',
    'qadaa_2739': 'محاكمة عقدية بين ابن تيمية وابن الهيتمي',
    'qadaa_3481': 'محاكمة دينية/تاريخية غير قضائية',
    'qadaa_7236': 'نقد أدبي لقصيدة النثر',
    'qadaa_8311': 'عنوان سياسي جدلي لا يمثل مادة قضائية',
    'qadaa_8700': 'عنوان نقدي/شخصي غير قضائي',
    'qadaa_8730': 'عنوان فكري/شخصي غير قضائي',
    'qadaa_9935': 'نص أدبي تراثي',
    'qadaa_11223': 'مقالة جدلية غير قضائية',
    'qadaa_11293': 'دراسة في محاكمة الأحمدين العقدية',
    'qadaa_11533': 'محاكمة حديثية بين الغماري وابن عاشور',
    'qadaa_11734': 'مناقضة بلاغية ومحاكمة عقلية',
    'rasail_13965': 'محاكمة تفسيرية بين المفسرين',
    'rasail_14090': 'دراسة في محاكمة الأحمدين العقدية',
    'alex_60966': 'عرض شخصيات وموضوعات بأسلوب أدبي',
    'archive_BBib-Alex-15168': 'مذكرات تاريخية عن محاكمة ثورة يوليو',
}


def stats_bucket(category: str) -> str:
    if category in {'القضاء الشرعي', 'المحاكم والمرافعات'}:
        return 'qadaa_count'
    if category == 'المحاماة والمرافعات':
        return 'mohama_count'
    return 'nizam_count'


with ITEMS_PATH.open(encoding='utf-8') as file:
    items = json.load(file)
with STATS_PATH.open(encoding='utf-8') as file:
    stats = json.load(file)

by_id = {item['id']: item for item in items}
missing_ids = sorted(set(REMOVALS) - set(by_id))
if missing_ids:
    raise RuntimeError(f'معرّفات الحذف غير موجودة: {missing_ids}')

removed_items = [by_id[item_id] for item_id in REMOVALS]
for item in removed_items:
    if not any(term in item.get('title', '') for term in ('محاكمة', 'المحاكمة')):
        raise RuntimeError(f"عنوان لا يطابق نطاق المراجعة: {item['id']} — {item['title']}")

remaining_items = [item for item in items if item['id'] not in REMOVALS]
for item in removed_items:
    bucket = stats_bucket(item.get('category', ''))
    stats[bucket] = int(stats.get(bucket, 0)) - 1

stats['total_items'] = len(remaining_items)
stats['last_updated'] = date.today().isoformat()

with ITEMS_PATH.open('w', encoding='utf-8') as file:
    json.dump(remaining_items, file, ensure_ascii=False, indent=2)
with PUBLIC_ITEMS_PATH.open('w', encoding='utf-8') as file:
    json.dump(remaining_items, file, ensure_ascii=False, indent=2)
with STATS_PATH.open('w', encoding='utf-8') as file:
    json.dump(stats, file, ensure_ascii=False, indent=2)

report = {
    'removed_count': len(removed_items),
    'removed_items': [
        {
            'id': item['id'],
            'title': item['title'],
            'category': item.get('category', ''),
            'source': item.get('source', ''),
            'reason': REMOVALS[item['id']],
        }
        for item in removed_items
    ],
    'updated_stats': stats,
}
with REPORT_PATH.open('w', encoding='utf-8') as file:
    json.dump(report, file, ensure_ascii=False, indent=2)

print(json.dumps({
    'removed_count': report['removed_count'],
    'remaining_count': len(remaining_items),
    'updated_stats': stats,
}, ensure_ascii=False, indent=2))
