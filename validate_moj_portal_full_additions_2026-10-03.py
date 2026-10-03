#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIRST_BACKUP = ROOT / 'backups/moj_portal_official_2026-10-03'
SECOND_BACKUP = ROOT / 'backups/moj_portal_reference_catalogues_2026-10-03'
SOURCE = 'وزارة العدل السعودية — البوابة القانونية'
EXPECTED_NEW = {
  'moj_portal_report_089','moj_portal_report_088','moj_portal_report_087','moj_portal_report_086',
  'moj_portal_report_085','moj_portal_report_084','moj_portal_report_083','moj_portal_report_082',
  'moj_portal_dictionary_ar_en_001','moj_portal_criminal_procedure_001','moj_portal_sharia_pleadings_002',
  'moj_portal_judicial_decisions_index_001','moj_portal_circulars_index_001','moj_portal_bankruptcy_judgments_index_001',
}

def load_items(path):
    value = json.loads(path.read_text(encoding='utf-8'))
    return value.get('items', value) if isinstance(value, dict) else value

def stable_sha(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

main_text = (ROOT/'items.json').read_text(encoding='utf-8')
public_text = (ROOT/'client/public/items.json').read_text(encoding='utf-8')
stats_text = (ROOT/'stats.json').read_text(encoding='utf-8')
public_stats_text = (ROOT/'client/public/stats.json').read_text(encoding='utf-8')
assert main_text == public_text, 'النسخة الرئيسية والمنشورة للمواد غير متطابقتين'
assert stats_text == public_stats_text, 'النسخة الرئيسية والمنشورة للإحصاءات غير متطابقتين'

before = load_items(FIRST_BACKUP/'items.before.json')
after_first = load_items(SECOND_BACKUP/'items.before.json')
after = load_items(ROOT/'items.json')
assert len(before) == 20055
assert len(after_first) == 20066
assert len(after) == 20069
before_by_id = {x['id']: x for x in before}
mid_by_id = {x['id']: x for x in after_first}
after_by_id = {x['id']: x for x in after}
assert len(before_by_id) == len(before) and len(mid_by_id) == len(after_first) and len(after_by_id) == len(after), 'تكرار في المعرّفات'
assert set(after_by_id) - set(before_by_id) == EXPECTED_NEW, 'إضافات غير معتمدة أو نقص في الإضافات'
assert not (set(before_by_id) - set(after_by_id)), 'حدث حذف في السجلات السابقة'
assert all(before_by_id[k] == after_by_id[k] for k in before_by_id), 'تغير سجل سابق'
assert set(after_by_id) - set(mid_by_id) == {
  'moj_portal_judicial_decisions_index_001','moj_portal_circulars_index_001','moj_portal_bankruptcy_judgments_index_001'
}, 'دمج الفهارس المرجعية غير مطابق'
assert sum(x.get('source') == SOURCE for x in after) == 20

stats = json.loads(stats_text)
assert stats['total_items'] == len(after) == 20069
assert stats['sources'][SOURCE] == 20
assert stats['material_types']['تقرير'] == 8
assert stats['material_types']['رابط مرجعي'] == 8
assert stats['qadaa_count'] + stats['nizam_count'] + stats['mohama_count'] == 20069
for stats_key, item_key in [('categories','category'),('sources','source'),('material_types','material_type'),('file_types','file_type')]:
    rebuilt = {}
    for item in after:
        value = str(item.get(item_key) or '').strip()
        if value:
            rebuilt[value] = rebuilt.get(value, 0) + 1
    assert stats[stats_key] == rebuilt, f'إحصاءات {stats_key} لا تطابق المواد'
assert stats['featured_count'] == sum(bool(x.get('is_featured')) for x in after)
assert stats['with_download_links'] == sum(int(x.get('download_links_count') or 0) > 0 for x in after)

cache = (ROOT/'client/src/hooks/useItems.ts').read_text(encoding='utf-8')
assert 'qadaa-moj-portal-catalogues-2026-10-03' in cache
for backup in [FIRST_BACKUP, SECOND_BACKUP]:
    manifest = json.loads((backup/'manifest.json').read_text(encoding='utf-8'))
    for name, expected in manifest['files'].items():
        actual = stable_sha((backup/name).read_text(encoding='utf-8'))
        assert actual == expected, f'فشل فحص بصمة النسخة الاحتياطية: {backup.name}/{name}'

result = {
  'before_total': 20055,
  'added_total': 14,
  'after_total': 20069,
  'official_source_total': 20,
  'report_total': 8,
  'reference_catalogue_total': 8,
  'hero_counts': {k: stats[k] for k in ['qadaa_count','nizam_count','mohama_count']},
  'data_sha256': stable_sha(main_text),
  'stats_sha256': stable_sha(stats_text),
  'validation': 'passed',
}
(ROOT/'moj_portal_full_additions_2026-10-03_validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
