import json
from pathlib import Path

ROOT = Path('/home/ubuntu/makanez-qadaa')
classified = json.loads((ROOT / 'ibrazx40_source_initial_classifications.json').read_text(encoding='utf-8'))['classifications']
records = {row['id']: row for row in json.loads((ROOT / 'ibrazx40_source_audit_records.json').read_text(encoding='utf-8'))['records']}
keywords = ['ايران','إيران','اسرائيل','إسرائيل','فلسطين','الحوث','انصار الله','أنصار الله','حزب الله','الاخوان','الإخوان','الثورة','القومية','اشتراكية','الشيوعية','الطائف','الشيع','ولاية الفقيه','التنظيم','الارهاب','الإرهاب','الصراع العربي','الامن الدولي','الأمن الدولي','النظام الدولي','الهيمنة','الاستراتيجية','السياسة الخارجية','العلاقات الدولية','الدولة']
queue = []
for row in classified:
    record = records[row['id']]
    haystack = ' '.join(str(record.get(key, '')) for key in ['title','category','author','investigator','publisher'])
    indicators = [key for key in keywords if key in haystack]
    if row['decision'] != 'KEEP' or indicators:
        queue.append({'record': record, 'initial': row, 'indicators': indicators})
output = {'total': len(queue), 'items': queue}
(ROOT / 'ibrazx40_critical_review_queue.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'queue_total': len(queue), 'initial_non_keep': sum(row['decision'] != 'KEEP' for row in classified), 'indicator_matches': sum(bool(item['indicators']) for item in queue)}, ensure_ascii=False))
