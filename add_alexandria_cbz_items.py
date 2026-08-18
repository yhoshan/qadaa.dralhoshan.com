import json
import re
from pathlib import Path

ROOT = Path('/home/ubuntu/makanez-qadaa')
ITEMS_PATH = ROOT / 'items.json'
PUBLIC_ITEMS_PATH = ROOT / 'client/public/items.json'
STATS_PATH = ROOT / 'client/public/stats.json'
READY_PATH = ROOT / 'alexandria_cbz_ready.json'
REPORT_PATH = ROOT / 'alexandria_cbz_add_report.json'
SOURCE_NAME = 'مكتبة الاسكندرية'

QADAA_CATEGORIES = {
    'القضاء والمحاكم', 'القضاء الإداري', 'القانون المدني', 'القانون الجنائي',
    'القانون التجاري', 'القانون الدولي', 'القانون العمالي', 'الأحوال الشخصية', 'التحكيم',
}

def normalize(value):
    value = (value or '').lower()
    value = value.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ى', 'ي').replace('ة', 'ه')
    return re.sub(r'[^\w\u0600-\u06ff]+', '', value)

def main():
    items = json.loads(ITEMS_PATH.read_text(encoding='utf-8'))
    ready = json.loads(READY_PATH.read_text(encoding='utf-8'))
    renamed = 0
    for item in items:
        if 'مكتبهالاسكندريه' in normalize(item.get('source', '')) and item.get('source') != SOURCE_NAME:
            item['source'] = SOURCE_NAME
            renamed += 1
    existing_ids = {item.get('id') for item in items}
    additions = [item for item in ready['ready'] if item['id'] not in existing_ids]
    items.extend(additions)

    stats = json.loads(STATS_PATH.read_text(encoding='utf-8'))
    stats['total'] = len(items)
    stats['total_items'] = len(items)
    stats['qadaa_count'] = int(stats.get('qadaa_count', 0)) + sum(1 for item in additions if item['category'] in QADAA_CATEGORIES)
    stats['nizam_count'] = int(stats.get('nizam_count', 0)) + sum(1 for item in additions if item['category'] == 'الأنظمة والتشريعات')
    stats['mohama_count'] = int(stats.get('mohama_count', stats.get('mohamah_count', 0))) + sum(1 for item in additions if item['category'] == 'المحاماة')
    stats['mohamah_count'] = stats['mohama_count']

    ITEMS_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')
    PUBLIC_ITEMS_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')
    STATS_PATH.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding='utf-8')
    report = {
        'source_name': SOURCE_NAME,
        'added': len(additions),
        'renamed_existing': renamed,
        'stats': stats,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))

if __name__ == '__main__':
    main()
