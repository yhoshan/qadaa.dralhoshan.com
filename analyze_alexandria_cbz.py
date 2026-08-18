import json
import re
from collections import Counter
from pathlib import Path

INPUT = Path('/home/ubuntu/Downloads/result.json')
ITEMS = Path('/home/ubuntu/makanez-qadaa/items.json')
OUTPUT = Path('/home/ubuntu/makanez-qadaa/alexandria_cbz_analysis.json')

LEGAL = re.compile(r'(قانون|نظام|لائحه|تشريع|قضاء|قضائي|محكم|حكم|دعوى|طعن|استئناف|نقض|مرافعات|محام|تنفيذ|اثبات|إثبات|تحكيم|تجاري|شركات|مدني|جنائي|جزائي|اداري|إداري|دستور|دولي|عمال|عمل|احوال شخصيه|أحوال شخصيه|عقود|التزام|تعويض|افلاس|إفلاس|ضريبه|ضرائب|جمارك|ملكيه|ملكية|وقف|مواريث|ارث|إرث|ديوان المظالم)', re.I)
EXCLUDE = re.compile(r'(القضاء والقدر|قضاء وقدر|قضاء الله|قضايا فلسفيه|قضيه وجود|قضيه لغويه|قضيه نحويه|قضيه ادبيه|محاكمه.*زمخشري|محاكمه.*شعر|محاكمه.*بلاغ)', re.I)

def clean_title(value):
    value = re.sub(r'^\d+[\s_\-]*', '', value or '')
    value = re.sub(r'\.(?:cbz|pdf|zip|rar|epub)$', '', value, flags=re.I)
    value = value.replace('_', ' ')
    value = re.sub(r'\s+', ' ', value).strip(' -–—.')
    return value[:400]

def normalize(value):
    value = (value or '').lower()
    value = value.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ى', 'ي').replace('ة', 'ه')
    return re.sub(r'[^\w\u0600-\u06ff]+', '', value)

def category(title):
    t = normalize(title)
    if any(x in t for x in ('محام', 'مذكرهدفاع')): return 'المحاماة'
    if any(x in t for x in ('تحكيم', 'محكم')): return 'التحكيم'
    if any(x in t for x in ('تجاري', 'شركات', 'افلاس', 'اوراقتجاريه')): return 'القانون التجاري'
    if any(x in t for x in ('مدني', 'التزام', 'عقود', 'ملكيه', 'تعويض')): return 'القانون المدني'
    if any(x in t for x in ('جنائي', 'جزائي', 'جريمه', 'عقوبات', 'قصاص')): return 'القانون الجنائي'
    if any(x in t for x in ('اداري', 'ديوانالمظالم', 'موظفعام')): return 'القضاء الإداري'
    if any(x in t for x in ('دولي', 'اتفاقيه', 'معاهده')): return 'القانون الدولي'
    if any(x in t for x in ('عمال', 'تأمينات', 'اجور')): return 'القانون العمالي'
    if any(x in t for x in ('احوالشخصيه', 'مواريث', 'ميراث', 'ارث', 'وقف')): return 'الأحوال الشخصية'
    if any(x in t for x in ('نظام', 'لائحه', 'تشريع', 'قرار', 'تعميم')): return 'الأنظمة والتشريعات'
    return 'القضاء والمحاكم'

def main():
    data = json.loads(INPUT.read_text(encoding='utf-8'))
    current = json.loads(ITEMS.read_text(encoding='utf-8'))
    existing_titles = {normalize(item.get('title')) for item in current}
    candidates, duplicates, excluded = [], [], []
    seen = set()
    for msg in data.get('messages', []):
        if not isinstance(msg, dict) or not msg.get('file_name'):
            continue
        title = clean_title(msg['file_name'])
        canonical = normalize(title)
        if not title or not LEGAL.search(title):
            continue
        if EXCLUDE.search(title):
            excluded.append({'id': msg.get('id'), 'title': title, 'reason': 'موضوع غير قضائي'})
            continue
        if canonical in seen:
            continue
        seen.add(canonical)
        record = {
            'id': msg.get('id'),
            'title': title,
            'file_name': msg.get('file_name'),
            'file_size': msg.get('file_size'),
            'file_type': msg.get('mime_type'),
            'telegram_link': f"https://t.me/c/1592768820/{msg.get('id')}",
            'category': category(title),
        }
        if canonical in existing_titles:
            duplicates.append(record)
        else:
            candidates.append(record)
    summary = {
        'source_name': 'مكتبة الإسكندرية الرسمية cbz',
        'source_url': 'https://t.me/c/1592768820/1',
        'total_messages': len(data.get('messages', [])),
        'files_total': sum(1 for msg in data.get('messages', []) if isinstance(msg, dict) and msg.get('file_name')),
        'legal_candidates_nonduplicate': len(candidates),
        'duplicates_exact': len(duplicates),
        'excluded_nonjudicial': len(excluded),
        'by_category': dict(Counter(item['category'] for item in candidates)),
        'candidates_sample': candidates[:100],
        'duplicates_sample': duplicates[:100],
        'excluded_sample': excluded[:100],
    }
    OUTPUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({
        'files_total': summary['files_total'],
        'legal_candidates_nonduplicate': summary['legal_candidates_nonduplicate'],
        'duplicates_exact': summary['duplicates_exact'],
        'excluded_nonjudicial': summary['excluded_nonjudicial'],
        'by_category': summary['by_category'],
    }, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
