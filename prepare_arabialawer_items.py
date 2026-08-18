import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path('/home/ubuntu/makanez-qadaa')
CANDIDATES_PATH = ROOT / 'arabialawer_material_candidates.json'
ITEMS_PATH = ROOT / 'items.json'
OUTPUT_PATH = ROOT / 'arabialawer_ready.json'

GENERIC_START = re.compile(r'^(كتاب|موسوعة|شرح|دراسة|رسالة|بحث|المجلد|الجزء|الوجيز|مدخل)\s+', re.I)
AUTHOR_SPLIT = re.compile(r'(?:\s*[-–—.]?\s*(?:تأليف|المؤلف(?:ون)?|اعداد|إعداد)\s*[:：]?)', re.I)

def normalize(value):
    value = (value or '').lower()
    value = value.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ى', 'ي').replace('ة', 'ه')
    value = re.sub(r'[^\w\u0600-\u06ff]+', '', value)
    return value

def simple_prefix(title):
    title = GENERIC_START.sub('', title.strip())
    return normalize(title)[:24]

def clean_title(value):
    value = re.sub(r'\s*\.pdf\s*$', '', value, flags=re.I)
    value = re.sub(r'\s+', ' ', value).strip(' .-–—_')
    return value[:360]

def extract_author(title):
    parts = AUTHOR_SPLIT.split(title, maxsplit=1)
    if len(parts) == 3:
        return parts[0].strip(), parts[2].strip(' .-–—')[:180]
    return title, ''

def category_for(title):
    t = title.lower().replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ى', 'ي').replace('ة', 'ه')
    if any(word in t for word in ('محاماه', 'محامي', 'مذكره دفاع', 'صياغه قانونيه')):
        return 'المحاماة'
    if any(word in t for word in ('تحكيم', 'محكم')):
        return 'التحكيم'
    if any(word in t for word in ('دولي', 'اتفاقيه', 'معاهده', 'انساني', 'الفضاء الخارجي', 'اعالي البحار')):
        return 'القانون الدولي'
    if any(word in t for word in ('تجاري', 'شركات', 'أوراق تجارية', 'إفلاس', 'بحري')):
        return 'القانون التجاري'
    if any(word in t for word in ('مدني', 'التزام', 'عقود', 'ملكيه', 'شفعه', 'تعويض')):
        return 'القانون المدني'
    if any(word in t for word in ('جنائي', 'جزائي', 'جريمة', 'عقوبات', 'مخدرات', 'متهم')):
        return 'القانون الجنائي'
    if any(word in t for word in ('اداري', 'ديوان المظالم', 'موظف عام')):
        return 'القضاء الإداري'
    if any(word in t for word in ('عمال', 'عمل', 'تامينات', 'اجر')):
        return 'القانون العمالي'
    if any(word in t for word in ('احوال شخصيه', 'اسره', 'زواج', 'طلاق', 'ميراث', 'تركات')):
        return 'الأحوال الشخصية'
    if any(word in t for word in ('نظام', 'لائحه', 'تشريع', 'قرار', 'تعميم')):
        return 'الأنظمة والتشريعات'
    return 'القضاء والمحاكم'

def material_type_for(title):
    normalized = title.lower().replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ى', 'ي').replace('ة', 'ه')
    if 'مجله' in normalized:
        return 'مجلة'
    if 'رساله' in normalized:
        return 'رسالة علمية'
    if 'موسوعه' in normalized:
        return 'موسوعة'
    if 'دليل' in normalized:
        return 'دليل'
    if 'مبادئ' in normalized or 'احكام' in normalized:
        return 'أحكام'
    if 'لائحه' in normalized or 'نظام' in normalized:
        return 'نظام'
    if 'بحث' in normalized or 'دراسه' in normalized:
        return 'بحث'
    return 'كتاب'

def main():
    candidates = json.loads(CANDIDATES_PATH.read_text(encoding='utf-8'))['candidates']
    existing = json.loads(ITEMS_PATH.read_text(encoding='utf-8'))
    existing_exact = {normalize(item.get('title', '')) for item in existing}
    existing_prefixes = defaultdict(list)
    for item in existing:
        title = item.get('title', '')
        existing_prefixes[simple_prefix(title)].append((item.get('id'), title, normalize(title)))

    accepted, duplicates, excluded, batch_exact = [], [], [], set()
    for candidate in candidates:
        raw_title = clean_title(candidate['title'])
        title, author = extract_author(raw_title)
        norm_title = normalize(title)
        if len(norm_title) < 12:
            excluded.append({'id': candidate['id'], 'title': raw_title, 'reason': 'عنوان قصير أو غير محدد'})
            continue
        if norm_title in existing_exact or norm_title in batch_exact:
            duplicates.append({'id': candidate['id'], 'title': raw_title, 'reason': 'تطابق عنوان مباشر'})
            continue
        potential = existing_prefixes.get(simple_prefix(title), [])
        is_duplicate = False
        for existing_id, existing_title, existing_norm in potential:
            shortest = min(len(norm_title), len(existing_norm))
            if shortest >= 20 and (norm_title in existing_norm or existing_norm in norm_title):
                duplicates.append({'id': candidate['id'], 'title': raw_title, 'reason': 'تطابق عنوان موسع', 'existing_id': existing_id, 'existing_title': existing_title})
                is_duplicate = True
                break
        if is_duplicate:
            continue
        batch_exact.add(norm_title)
        direct = candidate['direct_links'][0] if candidate['direct_links'] else ''
        accepted.append({
            'id': f"arabialawer_{candidate['id']}",
            'title': title,
            'author': author,
            'investigator': '',
            'link_telegram': candidate['telegram_link'],
            'link_drive': '',
            'link_direct': direct,
            'source': 'أكاديمية المحاماة',
            'category': category_for(title),
            'material_type': material_type_for(title),
            'file_type': 'PDF',
            'file_size': '',
            'pages_count': '',
            'is_featured': False,
            'download_links_count': 1,
        })
    result = {
        'source_name': 'أكاديمية المحاماة',
        'source_url': 'https://t.me/arabialawer',
        'accepted_count': len(accepted),
        'duplicates_count': len(duplicates),
        'excluded_count': len(excluded),
        'accepted': accepted,
        'duplicates_sample': duplicates[:500],
        'excluded_sample': excluded[:500],
    }
    OUTPUT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'accepted': len(accepted), 'duplicates': len(duplicates), 'excluded': len(excluded)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
