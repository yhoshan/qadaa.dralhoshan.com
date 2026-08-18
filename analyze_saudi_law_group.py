import json
import re
from collections import Counter
from pathlib import Path

INPUT = Path('/home/ubuntu/upload/pasted_file_aWMBHj_result.json')
OUTPUT = Path('/home/ubuntu/makanez-qadaa/saudi_law_group_analysis.json')

URL_RE = re.compile(r'https?://[^\s<>"\]]+', re.I)
KEYWORDS = re.compile(
    r'(نظام|لائحة|قرار|تعميم|وزارة العدل|ناجز|محكمة|قضاء|تنفيذ|استئناف|مرافعات|محاماة|وكالة|توثيق|عقد|تجاري|عمالي|جزائي|إداري|قانون)',
    re.I,
)
QUESTION_RE = re.compile(r'(\?|؟|كيف|هل |ماهي|وش |لو سمحت|استفسار|ساعد|افيدوني|عندي قضية|اريد)', re.I)
CHAT_RE = re.compile(r'^(شكرا|مشكور|جزاك|وعليكم السلام|نرد|صحيح|نعم|لا|الله يعين)', re.I)

def as_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        chunks = []
        for part in value:
            if isinstance(part, str):
                chunks.append(part)
            elif isinstance(part, dict):
                chunks.append(str(part.get('text', '')))
        return ''.join(chunks)
    return ''

def main():
    data = json.loads(INPUT.read_text(encoding='utf-8'))
    messages = data.get('messages', [])
    field_counts = Counter()
    candidates = []
    all_urls = Counter()

    for msg in messages:
        if not isinstance(msg, dict):
            continue
        for key in ('file', 'media_type', 'photo', 'thumbnail', 'mime_type'):
            if msg.get(key):
                field_counts[key] += 1

        text = as_text(msg.get('text')).strip()
        urls = URL_RE.findall(text)
        for url in urls:
            all_urls[url] += 1
        if not text:
            continue

        has_file = bool(msg.get('file') or msg.get('media_type') in {'document', 'video_file', 'audio_file'})
        is_structured_link = bool(urls) and bool(KEYWORDS.search(text)) and not QUESTION_RE.search(text)
        is_file_candidate = has_file and bool(KEYWORDS.search(text)) and not QUESTION_RE.search(text)
        if (is_structured_link or is_file_candidate) and not CHAT_RE.search(text):
            candidates.append({
                'id': msg.get('id'),
                'date': msg.get('date'),
                'from': msg.get('from'),
                'text': text[:2000],
                'urls': urls,
                'has_file': has_file,
                'file_name': msg.get('file'),
                'media_type': msg.get('media_type'),
            })

    result = {
        'group_name': data.get('name'),
        'group_type': data.get('type'),
        'group_id': data.get('id'),
        'messages_total': len(messages),
        'media_field_counts': dict(field_counts),
        'unique_urls': len(all_urls),
        'top_urls': [{'url': url, 'count': count} for url, count in all_urls.most_common(100)],
        'structured_candidates_count': len(candidates),
        'structured_candidates': candidates,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({
        'messages_total': result['messages_total'],
        'media_field_counts': result['media_field_counts'],
        'unique_urls': result['unique_urls'],
        'structured_candidates_count': result['structured_candidates_count'],
    }, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
