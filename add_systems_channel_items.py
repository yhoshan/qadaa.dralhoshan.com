import json
from pathlib import Path

ROOT = Path('/home/ubuntu/makanez-qadaa')
ITEMS = ROOT / 'items.json'
PUBLIC_ITEMS = ROOT / 'client/public/items.json'
STATS = ROOT / 'client/public/stats.json'
READY = ROOT / 'systems_channel_final.json'
REPORT = ROOT / 'systems_channel_add_report.json'

def main():
    items = json.loads(ITEMS.read_text(encoding='utf-8'))
    ready = json.loads(READY.read_text(encoding='utf-8'))
    existing_ids = {item.get('id') for item in items}
    additions = [item for item in ready['ready'] if item.get('id') not in existing_ids]
    items.extend(additions)
    stats = json.loads(STATS.read_text(encoding='utf-8'))
    stats['total'] = len(items)
    stats['total_items'] = len(items)
    stats['nizam_count'] = int(stats.get('nizam_count', 0)) + len(additions)
    ITEMS.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')
    PUBLIC_ITEMS.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')
    STATS.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding='utf-8')
    report = {'source_name': 'قناة الأنظمة', 'added': len(additions), 'stats': stats}
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))

if __name__ == '__main__':
    main()
