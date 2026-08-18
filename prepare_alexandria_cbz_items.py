import json
import re
from collections import defaultdict, Counter
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path('/home/ubuntu/makanez-qadaa')
INPUT = Path('/home/ubuntu/Downloads/result.json')
ITEMS = ROOT / 'items.json'
READY = ROOT / 'alexandria_cbz_ready.json'

LEGAL = re.compile(r'(قانون|نظام|لائحه|تشريع|قضاء|قضائي|محكم|حكم|دعوى|طعن|استئناف|نقض|مرافعات|محام|تنفيذ|اثبات|إثبات|تحكيم|تجاري|شركات|مدني|جنائي|جزائي|اداري|إداري|دستور|دولي|عمال|عمل|احوال شخصيه|أحوال شخصيه|عقود|التزام|تعويض|افلاس|إفلاس|ضريبه|ضرائب|جمارك|ملكيه|ملكية|وقف|مواريث|ارث|إرث|ديوان المظالم)', re.I)
EXCLUDE = re.compile(r'(القضاء والقدر|قضاء وقدر|قضاء الله|قضايا فلسفيه|قضيه وجود|قضيه لغويه|قضيه نحويه|قضيه ادبيه|محاكمه.*زمخشري|محاكمه.*شعر|محاكمه.*بلاغ)', re.I)
SOURCE_NAME = 'مكتبة الاسكندرية'

def clean_title(value):
    value = re.sub(r'^\d+[\s_\-]*', '', value or '')
    value = re.sub(r'\.(?:cbz|pdf|zip|rar|epub)$', '', value, flags=re.I)
    value = value.replace('_', ' ')
    return re.sub(r'\s+', ' ', value).strip(' -–—.')[:400]

def normalize(value):
    value = (value or '').lower()
    value = value.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ى', 'ي').replace('ة', 'ه')
    return re.sub(r'[^\w\u0600-\u06ff]+', '', value)

def prefix(value):
    value = re.sub(r'^(كتاب|شرح|دراسه|بحث|رساله|موسوعه|الجزء|المجلد)\s+', '', value.strip(), flags=re.I)
    return normalize(value)[:24]

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

def material_type(title):
    t = normalize(title)
    if 'موسوعه' in t: return 'موسوعة'
    if 'رساله' in t: return 'رسالة علمية'
    if 'مجله' in t: return 'مجلة'
    if 'نظام' in t or 'لائحه' in t: return 'نظام'
    if 'احكام' in t or 'مبادئ' in t: return 'أحكام'
    if 'دراسه' in t or 'بحث' in t: return 'بحث'
    return 'كتاب'

def main():
    source = json.loads(INPUT.read_text(encoding='utf-8'))
    items = json.loads(ITEMS.read_text(encoding='utf-8'))
    # توحيد تسمية الاستيراد السابق من الإسكندرية.
    renamed = 0
    for item in items:
        if 'مكتبهالاسكندريه' in normalize(item.get('source', '')):
            if item.get('source') != SOURCE_NAME:
                item['source'] = SOURCE_NAME
                renamed += 1
    existing_exact = {normalize(item.get('title')) for item in items}
    existing_by_prefix = defaultdict(list)
    for item in items:
        norm = normalize(item.get('title'))
        existing_by_prefix[prefix(item.get('title', ''))].append((item.get('id'), item.get('title', ''), norm))

    ready, duplicates_exact, duplicates_similar, excluded = [], [], [], []
    batch_titles = set()
    for msg in source.get('messages', []):
        if not isinstance(msg, dict) or not msg.get('file_name'):
            continue
        title = clean_title(msg['file_name'])
        norm = normalize(title)
        if not title or not LEGAL.search(title):
            continue
        if EXCLUDE.search(title):
            excluded.append({'id': msg.get('id'), 'title': title, 'reason': 'موضوع غير قضائي'})
            continue
        if norm in batch_titles or norm in existing_exact:
            duplicates_exact.append({'id': msg.get('id'), 'title': title})
            continue
        similar = None
        for existing_id, existing_title, existing_norm in existing_by_prefix.get(prefix(title), []):
            shorter = min(len(norm), len(existing_norm))
            ratio = SequenceMatcher(None, norm, existing_norm).ratio()
            if (shorter >= 24 and (norm in existing_norm or existing_norm in norm)) or (shorter >= 32 and ratio >= 0.965):
                similar = {'id': msg.get('id'), 'title': title, 'existing_id': existing_id, 'existing_title': existing_title, 'ratio': round(ratio, 4)}
                break
        if similar:
            duplicates_similar.append(similar)
            continue
        batch_titles.add(norm)
        ready.append({
            'id': f"alexandria_cbz_{msg.get('id')}",
            'title': title,
            'author': '',
            'investigator': '',
            'link_telegram': f"https://t.me/c/1592768820/{msg.get('id')}",
            'link_drive': '',
            'link_direct': '',
            'source': SOURCE_NAME,
            'category': category(title),
            'material_type': material_type(title),
            'file_type': 'CBZ',
            'file_size': f"{round((msg.get('file_size') or 0) / (1024 * 1024), 1)} MB" if msg.get('file_size') else '',
            'pages_count': '',
            'is_featured': False,
            'download_links_count': 1,
        })
    output = {
        'source_name': SOURCE_NAME,
        'source_url': 'https://t.me/c/1592768820/1',
        'renamed_existing_count': renamed,
        'ready_count': len(ready),
        'duplicates_exact_count': len(duplicates_exact),
        'duplicates_similar_count': len(duplicates_similar),
        'excluded_count': len(excluded),
        'by_category': dict(Counter(item['category'] for item in ready)),
        'ready': ready,
        'duplicates_similar_sample': duplicates_similar[:300],
    }
    READY.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: output[k] for k in ('renamed_existing_count', 'ready_count', 'duplicates_exact_count', 'duplicates_similar_count', 'excluded_count', 'by_category')}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
