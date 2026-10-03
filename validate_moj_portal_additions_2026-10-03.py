#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / 'backups/moj_portal_official_2026-10-03'
CANDIDATES = json.loads((ROOT / 'moj_portal_additions_2026-10-03_candidates.json').read_text(encoding='utf-8'))
EXPECTED_IDS = {item['id'] for item in CANDIDATES}
SOURCE = 'وزارة العدل السعودية — البوابة القانونية'
CACHE = 'qadaa-moj-portal-official-2026-10-03'


def read_json(path: Path):
    value = json.loads(path.read_text(encoding='utf-8'))
    return value['items'] if isinstance(value, dict) and isinstance(value.get('items'), list) else value


def sha(value: str):
    return hashlib.sha256(value.encode()).hexdigest()

main_text = (ROOT / 'items.json').read_text(encoding='utf-8')
public_text = (ROOT / 'client/public/items.json').read_text(encoding='utf-8')
stats_text = (ROOT / 'stats.json').read_text(encoding='utf-8')
public_stats_text = (ROOT / 'client/public/stats.json').read_text(encoding='utf-8')
assert main_text == public_text, 'تطابق المواد الرئيسة والمنشورة فشل'
assert stats_text == public_stats_text, 'تطابق الإحصاءات الرئيسة والمنشورة فشل'

before = read_json(BACKUP / 'items.before.json')
after = read_json(ROOT / 'items.json')
assert len(before) == 20055, len(before)
assert len(after) == 20066, len(after)
before_by_id = {item['id']: item for item in before}
after_by_id = {item['id']: item for item in after}
assert len(before_by_id) == len(before), 'تكرار سابق للمعرفات'
assert len(after_by_id) == len(after), 'تكرار لاحق للمعرفات'
assert set(after_by_id) - set(before_by_id) == EXPECTED_IDS, 'الإضافات الفعلية لا تطابق المرشحين المعتمدين'
assert set(before_by_id) - set(after_by_id) == set(), 'حدث حذف لسجل سابق'
assert all(before_by_id[k] == after_by_id[k] for k in before_by_id), 'تغيّر سجل سابق'
assert all(after_by_id[k] == candidate for k, candidate in {x['id']:x for x in CANDIDATES}.items()), 'سجل مضاف لا يطابق المرشح'
assert sum(item.get('source') == SOURCE for item in after) == 17, 'عدد سجلات المصدر الرسمي غير متوقع'

stats = json.loads(stats_text)
assert stats['total_items'] == len(after) == 20066
for field in ['categories','sources','material_types','file_types']:
    rebuilt = {}
    key = {'categories':'category','sources':'source','material_types':'material_type','file_types':'file_type'}[field]
    for item in after:
        value = str(item.get(key) or '').strip()
        if value:
            rebuilt[value] = rebuilt.get(value, 0) + 1
    assert stats[field] == dict(sorted(rebuilt.items(), key=lambda pair: (-pair[1], pair[0]))), f'عدم تطابق {field}'
assert stats['featured_count'] == sum(bool(item.get('is_featured')) for item in after)
assert stats['with_download_links'] == sum(int(item.get('download_links_count') or 0) > 0 for item in after)
assert stats['qadaa_count'] + stats['nizam_count'] + stats['mohama_count'] == stats['total_items']
assert stats['sources'][SOURCE] == 17
assert stats['material_types']['تقرير'] == 8

cache = (ROOT / 'client/src/hooks/useItems.ts').read_text(encoding='utf-8')
assert CACHE in cache, 'معلمة كسر الكاش الجديدة غير موجودة'
manifest = json.loads((BACKUP / 'manifest.json').read_text(encoding='utf-8'))
for name, expected in manifest['files'].items():
    assert sha((BACKUP / name).read_text(encoding='utf-8')) == expected, f'فشل بصمة النسخة الاحتياطية: {name}'

out = {
    'before_total': len(before),
    'added_total': len(EXPECTED_IDS),
    'after_total': len(after),
    'added_ids': sorted(EXPECTED_IDS),
    'official_source_count_after': stats['sources'][SOURCE],
    'report_count_after': stats['material_types']['تقرير'],
    'data_files_sha256': sha(main_text),
    'stats_files_sha256': sha(stats_text),
    'backup_directory': str(BACKUP.relative_to(ROOT)),
    'validation': 'passed',
}
(ROOT / 'moj_portal_additions_2026-10-03_validation.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(out, ensure_ascii=False, indent=2))
