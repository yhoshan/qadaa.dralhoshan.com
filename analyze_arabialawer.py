import json
import re
from collections import Counter
from pathlib import Path

INPUT = Path('/home/ubuntu/upload/pasted_file_ecVfMa_result.json')
OUTPUT = Path('/home/ubuntu/makanez-qadaa/arabialawer_analysis.json')

LEGAL = re.compile(r'(قانون|نظام|لائحة|قرار|قضاء|محكمة|حكم|طعن|استئناف|نقض|دعوى|مرافعات|محاماة|عقد|عقود|تنفيذ|إثبات|اثبات|تحكيم|تجاري|عمال|جزائ|إداري|حقوق|دستور|شركات|ضرائب|إفلاس|وكالة|توثيق)', re.I)
AD = re.compile(r'(دورة|تدريب|خصم|سجل الآن|اشترك|واتساب|تواصل|فرصة عمل|وظيفة|مدفوع|إعلان|للبيع|عرض خاص|استشارات)', re.I)
QUESTION = re.compile(r'(\?|؟|هل |كيف|متى|ما هو|ماهي|استفسار|ساعد)', re.I)
URL_RE = re.compile(r'https?://[^\s<>"\]]+', re.I)

def as_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return ''.join(part if isinstance(part, str) else str(part.get('text', '')) for part in value)
    return ''

def main():
    data = json.loads(INPUT.read_text(encoding='utf-8'))
    messages = data.get('messages', [])
    field_counts = Counter()
    selected = []
    urls = Counter()
    for msg in messages:
        if not isinstance(msg, dict):
            continue
        for key in ('file', 'media_type', 'photo', 'thumbnail', 'mime_type'):
            if msg.get(key):
                field_counts[key] += 1
        text = as_text(msg.get('text')).strip()
        for url in URL_RE.findall(text):
            urls[url] += 1
        if not text or AD.search(text) or QUESTION.search(text) or not LEGAL.search(text):
            continue
        has_file = bool(msg.get('file') or msg.get('media_type') in {'document', 'video_file', 'audio_file'})
        # منشور علمي مفصل أو ملف قانوني أو إحالة رسمية؛ لا يختار الملصقات والصور المجردة.
        if has_file or len(text) >= 350 or (URL_RE.search(text) and len(text) >= 100):
            selected.append({
                'id': msg.get('id'),
                'date': msg.get('date'),
                'from': msg.get('from'),
                'text': text[:6000],
                'text_length': len(text),
                'has_file': has_file,
                'file': msg.get('file'),
                'urls': URL_RE.findall(text),
            })
    result = {
        'channel_name': data.get('name'),
        'channel_type': data.get('type'),
        'channel_id': data.get('id'),
        'channel_url': 'https://t.me/arabialawer',
        'messages_total': len(messages),
        'media_field_counts': dict(field_counts),
        'unique_urls': len(urls),
        'structured_candidates_count': len(selected),
        'structured_candidates': selected,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('messages_total', 'media_field_counts', 'unique_urls', 'structured_candidates_count')}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
