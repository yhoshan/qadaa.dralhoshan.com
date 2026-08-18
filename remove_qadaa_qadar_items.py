import json
from datetime import date
from pathlib import Path

PROJECT = Path('/home/ubuntu/makanez-qadaa')
ITEMS_PATH = PROJECT / 'items.json'
PUBLIC_ITEMS_PATH = PROJECT / 'client/public/items.json'
STATS_PATH = PROJECT / 'client/public/stats.json'
REPORT_PATH = PROJECT / 'qadaa_qadar_removal_report.json'

REMOVE_IDS = {
    'risail_35344',
    'risail_51418',
    'buhooth_f1e6099b',
    'buhooth_79d615e1',
    'buhooth_12098889',
    'buhooth_f360bfa6',
    'buhooth_babe68e2',
    'buhooth_d956ed0d',
}

with ITEMS_PATH.open(encoding='utf-8') as file:
    items = json.load(file)
with STATS_PATH.open(encoding='utf-8') as file:
    stats = json.load(file)

removed = [item for item in items if item.get('id') in REMOVE_IDS]
found_ids = {item['id'] for item in removed}
if found_ids != REMOVE_IDS:
    raise RuntimeError(f'المعرّفات المطلوبة غير مكتملة: {sorted(REMOVE_IDS - found_ids)}')

for item in removed:
    title = item.get('title', '')
    if 'القضاء والقدر' not in title:
        raise RuntimeError(f"عنوان خارج نطاق الحذف: {item['id']} — {title}")

items = [item for item in items if item.get('id') not in REMOVE_IDS]
stats['total_items'] = len(items)
stats['qadaa_count'] = int(stats['qadaa_count']) - len(removed)
stats['research_count'] = int(stats.get('research_count', 0)) - sum(
    item.get('material_type') == 'بحث' for item in removed
)
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
