import json
from pathlib import Path

ROOT = Path('/home/ubuntu/makanez-qadaa')
ITEMS_PATH = ROOT / 'items.json'
PUBLIC_ITEMS_PATH = ROOT / 'client/public/items.json'
STATS_PATH = ROOT / 'client/public/stats.json'
READY_PATH = ROOT / 'saudi_law_group_ready.json'
REPORT_PATH = ROOT / 'saudi_law_group_add_report.json'

def main():
    items = json.loads(ITEMS_PATH.read_text(encoding='utf-8'))
    ready = json.loads(READY_PATH.read_text(encoding='utf-8'))
    accepted = ready['accepted']
    existing_ids = {item.get('id') for item in items}
    additions = [item for item in accepted if item['id'] not in existing_ids]
    items.extend(additions)

    stats = json.loads(STATS_PATH.read_text(encoding='utf-8'))
    stats['total'] = len(items)
    stats['total_items'] = len(items)
    stats['qadaa_count'] = int(stats.get('qadaa_count', 0)) + sum(1 for item in additions if 'قضاء' in item['category'] or 'محاكم' in item['category'])
    stats['nizam_count'] = int(stats.get('nizam_count', 0)) + sum(1 for item in additions if 'الأنظمة' in item['category'])
    stats['mohama_count'] = int(stats.get('mohama_count', stats.get('mohamah_count', 0))) + sum(1 for item in additions if 'محاماة' in item['category'])
    stats['mohamah_count'] = stats['mohama_count']

    ITEMS_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')
    PUBLIC_ITEMS_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')
    STATS_PATH.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding='utf-8')
    REPORT_PATH.write_text(json.dumps({
        'added': len(additions),
        'ids': [item['id'] for item in additions],
        'stats': stats,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'added': len(additions), 'total': stats['total'], 'qadaa': stats['qadaa_count'], 'nizam': stats['nizam_count'], 'mohama': stats['mohama_count']}, ensure_ascii=False))

if __name__ == '__main__':
    main()
