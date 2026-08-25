import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
records = json.loads((ROOT / 'iirmll_source_audit_records.json').read_text(encoding='utf-8'))['records']
initial = json.loads((ROOT / 'iirmll_source_initial_classifications.json').read_text(encoding='utf-8'))['classifications']
initial_by_id = {row['id']: row for row in initial}

signals = [
    'الإخوان', 'اسلام سياسي', 'الإسلام السياسي', 'الجماعات الاسلامية', 'الجماعات الإسلامية', 'الأحزاب', 'حزب',
    'المعارضة', 'الثورة', 'ثورات', 'الحوثي', 'الحوثيون', 'أنصار الله', 'حزب الله', 'ايران', 'إيران',
    'ولاية الفقيه', 'الشيعة', 'التشيع', 'السنة والشيعة', 'الطائفية', 'التكفير', 'القومية', 'الناصرية',
    'الاشتراكية', 'الشيوعية', 'الماركسية', 'تنظيمات مسلحة', 'حركات سياسية', 'التحول الديمقراطي',
    'علاقات دولية', 'استراتيجية', 'استراتيجيات', 'مذكرات', 'سيرة ذاتية', 'تاريخ سياسي',
    'القضاء والقدر', 'الحكمة', 'نظام اجتماعي', 'نظام فكري', 'حقوق المرأة', 'العقود', 'الملكية',
]
queue = []
for record in records:
    title = str(record.get('title') or '')
    initial_row = initial_by_id[record['id']]
    lowered = title.lower()
    matched = [signal for signal in signals if signal.lower() in lowered]
    title_words = re.findall(r'\w+', title)
    triggers = []
    if initial_row['decision'] in {'REMOVE', 'REVIEW'}:
        triggers.append(f"initial_{initial_row['decision'].lower()}")
    if initial_row['confidence'] <= 78:
        triggers.append('low_confidence')
    if matched:
        triggers.append('sensitive_or_false_match_terms')
    if len(title_words) <= 3 or len(title.strip()) <= 17:
        triggers.append('very_short_title')
    if triggers:
        queue.append({
            'record': record,
            'initial': initial_row,
            'triggers': triggers,
            'matched_terms': matched,
        })
output = {'total_source_records': len(records), 'queue_count': len(queue), 'queue': queue}
(ROOT / 'iirmll_critical_review_queue.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'total_source_records': len(records), 'queue_count': len(queue)}, ensure_ascii=False, indent=2))
