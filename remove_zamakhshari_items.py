import json
from datetime import date
from pathlib import Path

PROJECT = Path('/home/ubuntu/makanez-qadaa')
ITEMS_PATH = PROJECT / 'items.json'
PUBLIC_ITEMS_PATH = PROJECT / 'client/public/items.json'
STATS_PATH = PROJECT / 'client/public/stats.json'
REPORT_PATH = PROJECT / 'zamakhshari_removal_report.json'

REMOVE_IDS = {'qadaa_1383', 'buhooth_54defb82'}

with ITEMS_PATH.open(encoding='utf-8') as file:
    items = json.load(file)
with STATS_PATH.open(encoding='utf-8') as file:
    stats = json.load(file)

removed = [item for item in items if item.get('id') in REMOVE_IDS]
found_ids = {item['id'] for item in removed}
if found_ids != REMOVE_IDS:
    raise RuntimeError(f'المعرّفات المطلوبة غير مكتملة: {sorted(REMOVE_IDS - found_ids)}')

for item in removed:
    if 'الزمخشري' not in ' '.join(str(item.get(key, '')) for key in ('title', 'author', 'investigator')):
        raise RuntimeError(f"عنصر خارج نطاق الحذف: {item['id']}")

items = [item for item in items if item.get('id') not in REMOVE_IDS]
stats['total_items'] = len(items)
stats['qadaa_count'] = int(stats['qadaa_count']) - 1
stats['research_count'] = int(stats.get('research_count', 0)) - 1
stats['last_updated'] = date.today().isoformat()

for path, data in ((ITEMS_PATH, items), (PUBLIC_ITEMS_PATH, items), (STATS_PATH, stats)):
    with path.open('w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

with REPORT_PATH.open('w', encoding='utf-8') as file:
    json.dump({
        'removed_count': len(removed),
        'removed_items': removed,
        'updated_stats': stats,
    }, file, ensure_ascii=False, indent=2)

print(json.dumps({'removed_count': len(removed), 'updated_stats': stats}, ensure_ascii=False, indent=2))
