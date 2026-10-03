#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / 'backups/jtc_qiyam_2026-10-03'
EXPECTED_IDS = {
  'jtc_judicial_training_conference_001','jtc_mediators_001','jtc_enforcement_001','jtc_notaries_001','jtc_lawyers_development_001',
  'qiyam_governance_001','qiyam_financial_compliance_001','qiyam_procurement_001','qiyam_wills_estates_001','qiyam_admin_cases_001','qiyam_contract_review_001',
}
SOURCES = {'مركز التدريب العدلي — وزارة العدل السعودية': 5, 'مكتبة قيم للقانون': 6}

def read_items(path):
    value = json.loads(path.read_text(encoding='utf-8'))
    return value.get('items', value) if isinstance(value, dict) else value

def sha(value): return hashlib.sha256(value.encode('utf-8')).hexdigest()

main_text = (ROOT/'items.json').read_text(encoding='utf-8')
public_text = (ROOT/'client/public/items.json').read_text(encoding='utf-8')
stats_text = (ROOT/'stats.json').read_text(encoding='utf-8')
public_stats_text = (ROOT/'client/public/stats.json').read_text(encoding='utf-8')
assert main_text == public_text, 'ملفا المواد الرئيس والمنشور غير متطابقين'
assert stats_text == public_stats_text, 'ملفا الإحصاءات الرئيس والمنشور غير متطابقين'

before = read_items(BACKUP/'items.before.json')
after = read_items(ROOT/'items.json')
before_map, after_map = ({item['id']: item for item in values} for values in (before, after))
assert len(before) == len(before_map) == 20069
assert len(after) == len(after_map) == 20080
assert set(after_map) - set(before_map) == EXPECTED_IDS, 'الإضافات الفعلية لا تطابق القائمة المعتمدة'
assert not (set(before_map) - set(after_map)), 'حذف غير مقصود في السجلات السابقة'
assert all(before_map[key] == after_map[key] for key in before_map), 'تغير غير مقصود في سجل سابق'
assert len(after_map) == len(after), 'تكرار معرّفات في البيانات النهائية'
assert {source: sum(item.get('source') == source for item in after) for source in SOURCES} == SOURCES
assert all(item.get('link_direct','').startswith('https://') for item in after if item['id'] in EXPECTED_IDS)

stats = json.loads(stats_text)
assert stats['total_items'] == len(after) == 20080
assert stats['qadaa_count'] + stats['nizam_count'] + stats['mohama_count'] == 20080
for stats_key, field in [('categories','category'),('sources','source'),('material_types','material_type'),('file_types','file_type')]:
    rebuilt = {}
    for item in after:
        value = str(item.get(field) or '').strip()
        if value: rebuilt[value] = rebuilt.get(value, 0) + 1
    assert stats[stats_key] == rebuilt, f'عدم تطابق إحصاءات {stats_key}'
assert stats['featured_count'] == sum(bool(item.get('is_featured')) for item in after)
assert stats['with_download_links'] == sum(int(item.get('download_links_count') or 0) > 0 for item in after)
assert 'qadaa-jtc-qiyam-2026-10-03' in (ROOT/'client/src/hooks/useItems.ts').read_text(encoding='utf-8')

manifest = json.loads((BACKUP/'manifest.json').read_text(encoding='utf-8'))
for name, expected_sha in manifest['files'].items():
    assert sha((BACKUP/name).read_text(encoding='utf-8')) == expected_sha, f'فشل فحص النسخة الاحتياطية: {name}'

result = {
  'before_total': len(before), 'added_total': len(EXPECTED_IDS), 'after_total': len(after),
  'source_counts': {source: sum(item.get('source') == source for item in after) for source in SOURCES},
  'hero_counts': {key: stats[key] for key in ['qadaa_count','nizam_count','mohama_count']},
  'data_sha256': sha(main_text), 'stats_sha256': sha(stats_text), 'validation': 'passed'
}
(ROOT/'jtc_qiyam_2026-10-03_validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
