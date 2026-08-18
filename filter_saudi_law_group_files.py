import json
import re
from pathlib import Path

INPUT = Path('/home/ubuntu/upload/pasted_file_aWMBHj_result.json')
OUTPUT = Path('/home/ubuntu/makanez-qadaa/saudi_law_group_file_candidates.json')

LEGAL = re.compile(
    r'(نظام|لائحة|قرار|تعميم|قضاء|محكمة|دعوى|مرافعات|استئناف|تنفيذ|محاماة|وكالة|توثيق|عقد|عقود|قانون|تجاري|عمال|جزائ|إثبات|اثبات|نيابة|ديوان المظالم|تقاضي|أحكام|مبادئ|تعويض|تحكيم|إفلاس|ضرائب|زكاة|شركات|سجل تجاري|نظامي|عدل|ناجز|حقوق)',
    re.I,
)
EXCLUDE = re.compile(
    r'(سيرة ذاتية|cv|شهادة حضور|إعلان|دورة|وظائف|تدريب|مطلوب|واتساب|استشارة|سؤال|استفسار|تسويق|عرض|محامي مرخص|فرصة|سجل حضور|محادثة|صورة|جدول دوام|تقرير طبي)',
    re.I,
)
QUESTION = re.compile(r'[؟?]|^(هل|كيف|ماهي|وش|لو|ممكن|عندي|ابغى|أبي|اريد|متى)', re.I)

def as_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = []
        for part in value:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict):
                parts.append(str(part.get('text', '')))
        return ''.join(parts)
    return ''

def clean_title(text):
    text = text.replace('\u2068', '').replace('\u2069', '')
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'\s+', ' ', text).strip(' -–—•*#\n\t')
    return text[:350]

def main():
    data = json.loads(INPUT.read_text(encoding='utf-8'))
    selected = []
    rejected = []
    seen_titles = set()
    for msg in data.get('messages', []):
        if not isinstance(msg, dict) or not msg.get('file'):
            continue
        title = clean_title(as_text(msg.get('text')))
        if len(title) < 8 or not LEGAL.search(title) or EXCLUDE.search(title) or QUESTION.search(title):
            rejected.append({'id': msg.get('id'), 'title': title})
            continue
        canonical = re.sub(r'[^\w\u0600-\u06ff]+', '', title.lower())
        if canonical in seen_titles:
            continue
        seen_titles.add(canonical)
        selected.append({
            'id': msg.get('id'),
            'date': msg.get('date'),
            'title': title,
            'from': msg.get('from'),
            'telegram_link': f"https://t.me/Lawyers_saudi/{msg.get('id')}",
        })
    result = {
        'source_name': 'قناة المحاماة والقانون السعودي',
        'source_public_url': 'https://t.me/Lawyers_saudi',
        'selected_count': len(selected),
        'rejected_file_messages_count': len(rejected),
        'selected': selected,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"selected={len(selected)} rejected={len(rejected)}")

if __name__ == '__main__':
    main()
