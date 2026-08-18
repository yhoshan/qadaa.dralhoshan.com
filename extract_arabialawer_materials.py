import json
import re
from pathlib import Path

INPUT = Path('/home/ubuntu/upload/pasted_file_ecVfMa_result.json')
OUTPUT = Path('/home/ubuntu/makanez-qadaa/arabialawer_material_candidates.json')

LEGAL = re.compile(r'(قانون|نظام|لائحة|قرار|قضاء|محكم|حكم|طعن|استئناف|نقض|دعوى|مرافعات|محاماة|عقد|التزام|تنفيذ|إثبات|اثبات|تحكيم|تجاري|عمال|جزائ|إداري|حقوق|دستور|شركات|ضرائب|إفلاس|وكالة|توثيق|مدني|جنائي|ملكية|شفعة|تعويض)', re.I)
MATERIAL = re.compile(r'(كتاب|موسوعة|شرح|مبادئ|أحكام|قانون|نظام|لائحة|دليل|محاضرة|ملخص|مذكرة|مرافعات|قضاء|قضائي|دعوى|عقود|التزام|تجاري|مدني|عمال|جزائ|دستور|تنفيذ|تحكيم|إفلاس|معجم|تشريع)', re.I)
EXCLUDE = re.compile(r'(دورة|تدريب|سجل الآن|واتساب|وظيفة|فرصة|إعلان|استشارة|استفسار|سؤال|مسودة|مشروع نظام|مشروع قانون|رسالة ماجستير مطلوب|لمن يريد|تهنئة|شهادة حضور|سيرة ذاتية|cv|طلب عمل|أسعار|عرض خاص)', re.I)
QUESTION = re.compile(r'[؟?]|^(هل|كيف|متى|ما هو|ماهي|لو|اريد|أريد|أرجو|ممكن|من يعرف)', re.I)
URL_RE = re.compile(r'https?://[^\s<>"\]]+', re.I)
FILE_HOST = re.compile(r'(mediafire\.com|drive\.google\.com|archive\.org|mega\.nz|4shared\.com|box\.com|dropbox\.com|\.pdf(?:[?#/]|$))', re.I)

def as_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return ''.join(part if isinstance(part, str) else str(part.get('text', '')) for part in value)
    return ''

def title_from(text):
    text = URL_RE.sub('', text)
    text = re.sub(r'\s+', ' ', text).strip(' -*_#•\n\t')
    for label in ('الاسم :', 'الاسم:', 'عنوان الكتاب:', 'الكتاب:'):
        if label in text:
            text = text.split(label, 1)[1].strip()
            break
    # الاسم أو العنوان غالباً في السطر الأول قبل تفاصيل المؤلف والروابط.
    text = re.split(r'(?:المؤلف\s*[:：]|رابط التحميل\s*[:：]|الجزء\s*(?:الاول|الأول|الثاني)\s*[:：])', text, maxsplit=1)[0].strip()
    return text[:420].strip(' .-–—')

def normalize(value):
    value = value.lower().replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ى', 'ي').replace('ة', 'ه')
    return re.sub(r'[^\w\u0600-\u06ff]+', '', value)

def main():
    data = json.loads(INPUT.read_text(encoding='utf-8'))
    selected, seen = [], set()
    for msg in data.get('messages', []):
        if not isinstance(msg, dict):
            continue
        text = as_text(msg.get('text')).strip()
        if not text:
            continue
        urls = URL_RE.findall(text)
        has_download_url = any(FILE_HOST.search(url) for url in urls)
        has_file = bool(msg.get('file'))
        if not (has_file or has_download_url):
            continue
        title = title_from(text)
        if len(title) < 10 or len(title) > 420 or not LEGAL.search(title) or not MATERIAL.search(title) or EXCLUDE.search(title) or QUESTION.search(title):
            continue
        canonical = normalize(title)
        if canonical in seen:
            continue
        seen.add(canonical)
        direct_links = [url for url in urls if FILE_HOST.search(url)]
        selected.append({
            'id': msg.get('id'),
            'date': msg.get('date'),
            'title': title,
            'from': msg.get('from'),
            'has_file': has_file,
            'direct_links': direct_links,
            'telegram_link': f"https://t.me/arabialawer/{msg.get('id')}",
        })
    result = {
        'source_name': 'أكاديمية المحاماة',
        'source_url': 'https://t.me/arabialawer',
        'candidates_count': len(selected),
        'candidates': selected,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'candidates_count': len(selected)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
