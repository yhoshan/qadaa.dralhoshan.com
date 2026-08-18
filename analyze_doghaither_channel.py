import json
import re
from collections import Counter
from pathlib import Path

INPUT = Path('/home/ubuntu/upload/pasted_file_xItVSF_result.json')
OUTPUT = Path('/home/ubuntu/makanez-qadaa/doghaither_channel_analysis.json')

LEGAL_TERMS = [
    'قضاء', 'قضائي', 'قاضي', 'قضاة', 'محكمة', 'محاكم', 'تحكيم', 'محام',
    'نظام', 'أنظمة', 'لائحة', 'لوائح', 'قانون', 'قوانين', 'نظامي',
    'دعوى', 'دعاوى', 'مرافعات', 'إثبات', 'بينات', 'تنفيذ', 'خصومة',
    'حكم', 'أحكام', 'عدالة', 'محضر', 'استئناف', 'اعتراض', 'قرار', 'قرارات',
    'قضية', 'قضايا', 'عقوبة', 'عقوبات', 'جريمة', 'جرائم', 'نيابة',
    'حقوق', 'حق ', 'التزام', 'التزامات', 'عقد', 'عقود', 'تجارة', 'تجاري',
    'مدني', 'جنائي', 'جزائي', 'دستوري', 'إداري', 'مالية', 'ملكية',
    'وقف', 'وصية', 'مواريث', 'طلاق', 'زواج', 'نفقة', 'أسرة'
]

EXCLUDE_TERMS = [
    'العقيدة', 'التوحيد', 'التفسير', 'الحديث', 'السيرة', 'الرقية',
    'الأذكار', 'رمضان', 'الحج', 'الصلاة', 'الزكاة', 'الصيام', 'فتاوى',
    'فتوى', 'دعاء', 'القرآن', 'القران', 'البخاري', 'مسلم', 'تجويد'
]

URL_RE = re.compile(r'https?://[^\s\]\["<>]+')

def flatten_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = []
        for node in value:
            if isinstance(node, str):
                parts.append(node)
            elif isinstance(node, dict):
                parts.append(str(node.get('text', '')))
        return ' '.join(parts)
    return ''

with INPUT.open(encoding='utf-8') as f:
    data = json.load(f)

messages = data.get('messages', [])
summary = Counter()
candidates = []
file_samples = []

for message in messages:
    if message.get('type') != 'message':
        continue
    summary['messages'] += 1
    text = flatten_text(message.get('text', '')).strip()
    file_name = message.get('file_name') or message.get('media_type') or ''
    if file_name:
        summary['with_files'] += 1
        if len(file_samples) < 30:
            file_samples.append({
                'id': message.get('id'),
                'file_name': file_name,
                'text': text[:500],
            })
    if not text and not file_name:
        continue

    lower = text.lower()
    legal_hits = [term for term in LEGAL_TERMS if term in lower]
    exclude_hits = [term for term in EXCLUDE_TERMS if term in lower]
    urls = URL_RE.findall(text)
    has_media = bool(file_name)

    # Retain direct legal materials and article/file posts, while excluding purely religious posts.
    if legal_hits and (has_media or urls or len(text) >= 35) and len(legal_hits) > len(exclude_hits):
        candidates.append({
            'message_id': message.get('id'),
            'date': message.get('date'),
            'text': text,
            'file_name': file_name,
            'urls': urls,
            'legal_hits': legal_hits,
            'exclude_hits': exclude_hits,
        })

result = {
    'channel_name': data.get('name'),
    'channel_type': data.get('type'),
    'channel_id': data.get('id'),
    'message_summary': dict(summary),
    'candidate_count': len(candidates),
    'candidates': candidates,
    'file_samples': file_samples,
}

with OUTPUT.open('w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(json.dumps({
    'channel': result['channel_name'],
    'messages': summary['messages'],
    'with_files': summary['with_files'],
    'candidate_count': len(candidates),
    'output': str(OUTPUT),
}, ensure_ascii=False, indent=2))

for candidate in candidates[:20]:
    preview = candidate['text'].replace('\n', ' ')[:180]
    print(f"[{candidate['message_id']}] {candidate['legal_hits']} :: {preview}")
