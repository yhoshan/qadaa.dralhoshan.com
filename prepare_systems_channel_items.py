import json
import re
from difflib import SequenceMatcher
from collections import defaultdict
from pathlib import Path

ROOT = Path('/home/ubuntu/makanez-qadaa')
INPUT = Path('/home/ubuntu/upload/pasted_file_VOOnTb_result.json')
ITEMS = ROOT / 'items.json'
OUTPUT = ROOT / 'systems_channel_ready.json'
SOURCE_NAME = 'قناة الأنظمة'

OFFICIAL = re.compile(r'^(?:نظام|اللائحه|اللائحة|الائحه|اللائحة التنفيذية|تنظيم|قواعد|ضوابط)\b', re.I)
EXCLUDE = re.compile(r'(ملخص|اختبار|اسئل[ةه]|واجب|محاضر[ةه]|دكتور|عرض|حلول|حل |جدول|تجميعات|واتس|شيت|تدريب|مشروع تخرج|مراجعه|نماذج|سلايدات|مذكره|فصل|الدوري|#|س:ج|الحقيبه|xmind|قديم|لاغي)', re.I)

def clean_title(value):
    value = re.sub(r'\.(?:pdf|docx?|xlsx?|pptx?|zip|rar|xmind)$', '', value or '', flags=re.I)
    value = value.replace('_', ' ')
    return re.sub(r'\s+', ' ', value).strip(' -–—.')[:360]

def normalize(value):
    value = (value or '').lower()
    value = value.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ى', 'ي').replace('ة', 'ه')
    return re.sub(r'[^\w\u0600-\u06ff]+', '', value)

def prefix(value):
    return normalize(value)[:28]

def main():
    raw = json.loads(INPUT.read_text(encoding='utf-8'))
    existing = json.loads(ITEMS.read_text(encoding='utf-8'))
    existing_exact = {normalize(item.get('title')) for item in existing}
    existing_by_prefix = defaultdict(list)
    for item in existing:
        norm = normalize(item.get('title'))
        existing_by_prefix[prefix(item.get('title', ''))].append((item.get('id'), item.get('title', ''), norm))

    ready, skipped, duplicates, seen = [], [], [], set()
    for msg in raw.get('messages', []):
        if not isinstance(msg, dict) or not msg.get('file_name'):
            continue
        title = clean_title(msg['file_name'])
        norm = normalize(title)
        if not OFFICIAL.search(title) or EXCLUDE.search(title) or len(norm) < 12:
            continue
        if norm in seen or norm in existing_exact:
            duplicates.append({'id': msg.get('id'), 'title': title, 'reason': 'تطابق مباشر'})
            continue
        similar = None
        for existing_id, existing_title, existing_norm in existing_by_prefix.get(prefix(title), []):
            short = min(len(norm), len(existing_norm))
            ratio = SequenceMatcher(None, norm, existing_norm).ratio()
            if (short >= 24 and (norm in existing_norm or existing_norm in norm)) or (short >= 30 and ratio >= 0.965):
                similar = {'id': msg.get('id'), 'title': title, 'existing_id': existing_id, 'existing_title': existing_title, 'ratio': round(ratio, 4)}
                break
        if similar:
            duplicates.append(similar)
            continue
        seen.add(norm)
        ready.append({
            'id': f"systems_channel_{msg.get('id')}",
            'title': title,
            'author': '',
            'investigator': '',
            'link_telegram': f"https://t.me/c/1197187841/{msg.get('id')}",
            'link_drive': '',
            'link_direct': '',
            'source': SOURCE_NAME,
            'category': 'الأنظمة والتشريعات',
            'material_type': 'نظام' if normalize(title).startswith('نظام') else 'لائحة',
            'file_type': 'PDF',
            'file_size': f"{round((msg.get('file_size') or 0) / (1024 * 1024), 1)} MB" if msg.get('file_size') else '',
            'pages_count': '',
            'is_featured': False,
            'download_links_count': 1,
        })
    result = {
        'source_name': SOURCE_NAME,
        'channel_name': raw.get('name'),
        'ready_count': len(ready),
        'duplicates_count': len(duplicates),
        'ready': ready,
        'duplicates_sample': duplicates[:200],
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'ready_count': len(ready), 'duplicates_count': len(duplicates)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
