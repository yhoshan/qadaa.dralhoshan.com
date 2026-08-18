import json
import re
from pathlib import Path

INPUT = Path('/home/ubuntu/upload/pasted_file_VOOnTb_result.json')
OUTPUT = Path('/home/ubuntu/makanez-qadaa/systems_channel_analysis.json')

SYSTEMS = re.compile(r'(نظام|انظمه|أنظمة|لائحه|لائحة|لوائح|قرار|تعميم|تشريع|ضريب|زكا[ةه]|جمارك|تجاري|شركات|افلاس|إفلاس|استثمار|منافس[ةه]|سوق المال|تأمين|عمال|عمل|بيئ[ةه]|تمويل|محاسب[ةه]|مراجع[ةه]|هيئ[ةه]|حوكم[ةه]|ملكي[ةه] فكري[ةه]|غسل|مخالفات)', re.I)
EXCLUDE = re.compile(r'(ملخص|اختبار|اسئل[ةه]|واجب|محاضر[ةه]|دكتور|عرض|حلول|حل |جدول|تجميعات|تليجرام|واتس|شيت|تدريب|مشروع تخرج|مراجعه اختبار|نماذج اختبار|سلايدات|مذكره)', re.I)
GENERIC = re.compile(r'^(?:bl|reg|chapter|unit|file|scan|img|image|doc|pdf)[\s_\-\d.]*$', re.I)

def clean_title(value):
    value = re.sub(r'\.(?:pdf|docx?|xlsx?|pptx?|zip|rar)$', '', value or '', flags=re.I)
    value = value.replace('_', ' ')
    return re.sub(r'\s+', ' ', value).strip(' -–—.')[:360]

def main():
    data = json.loads(INPUT.read_text(encoding='utf-8'))
    selected, seen = [], set()
    files = 0
    for msg in data.get('messages', []):
        if not isinstance(msg, dict) or not msg.get('file_name'):
            continue
        files += 1
        title = clean_title(msg['file_name'])
        canonical = re.sub(r'[^\w\u0600-\u06ff]+', '', title.lower())
        if not title or len(canonical) < 12 or GENERIC.match(title) or not SYSTEMS.search(title) or EXCLUDE.search(title):
            continue
        if canonical in seen:
            continue
        seen.add(canonical)
        selected.append({
            'id': msg.get('id'),
            'title': title,
            'file_name': msg.get('file_name'),
            'file_size': msg.get('file_size'),
            'mime_type': msg.get('mime_type'),
            'telegram_link': f"https://t.me/c/1197187841/{msg.get('id')}",
        })
    result = {
        'source_name': 'قناة الأنظمة',
        'channel_name': data.get('name'),
        'channel_id': data.get('id'),
        'messages_total': len(data.get('messages', [])),
        'files_total': files,
        'system_candidates_count': len(selected),
        'candidates': selected,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('messages_total', 'files_total', 'system_candidates_count')}, ensure_ascii=False))

if __name__ == '__main__':
    main()
