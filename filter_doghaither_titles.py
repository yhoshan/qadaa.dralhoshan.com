import json
import re
from pathlib import Path
from urllib.parse import urlparse

ANALYSIS = Path('/home/ubuntu/makanez-qadaa/doghaither_channel_analysis.json')
ITEMS = Path('/home/ubuntu/makanez-qadaa/items.json')
OUTPUT = Path('/home/ubuntu/makanez-qadaa/doghaither_legal_candidates.json')

ALLOWED_HOSTS = {'www.alukah.net', 'alukah.net'}
TITLE_TERMS = [
    'قضاء', 'قضائي', 'محكمة', 'محاكم', 'قاضي', 'قضاة', 'عدالة', 'دعوى', 'دعاوى',
    'تحكيم', 'محام', 'مرافعات', 'تنفيذ', 'استئناف', 'خصومة', 'نظام', 'أنظمة', 'نظامي',
    'لائحة', 'لوائح', 'قانون', 'قانوني', 'تجاري', 'مدني', 'جنائي', 'جزائي', 'إداري',
    'دستوري', 'منافسة', 'حقوق', 'التزام', 'عقد', 'عقود', 'إثبات', 'بينات', 'عقار',
    'ملكية', 'تعويض', 'مسؤولية', 'جريمة', 'جرائم', 'عقوبة', 'عقوبات', 'وقف', 'وصية',
    'مواريث', 'نفقة', 'طلاق', 'حضانة', 'زواج', 'أسرة'
]
OUT_OF_SCOPE = [
    'التوحيد', 'العقيدة', 'التفسير', 'القرآن', 'القران', 'الحديث', 'السيرة', 'رمضان',
    'الصلاة', 'الصيام', 'الحج', 'الزكاة', 'الأذكار', 'الدعاء', 'الرقية', 'تجويد',
    'قراءات', 'الشعر'
]

def canonical(url):
    parsed = urlparse(url)
    return f'{parsed.scheme.lower()}://{parsed.netloc.lower()}{parsed.path.rstrip("/")}/'

def title_from_post(text):
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'^\s*د\.?\s*عبدالعزيز\s*الدغيثر\s*دكتوراه\s*في\s*القانون\s*التجاري\.\s*محامي\.?:?\s*', '', text, flags=re.I)
    text = re.sub(r'^\s*د\.عبدالعزيزالدغيثر\s*دكتوراه\s*في\s*القانون\s*التجاري\.\s*محامي\.?:?\s*', '', text, flags=re.I)
    text = re.sub(r'\(PDF\)', '', text, flags=re.I)
    lines = [re.sub(r'\s+', ' ', line).strip(' -–:') for line in text.splitlines()]
    lines = [line for line in lines if line and not line.startswith('#')]
    title = lines[0] if lines else ''
    return title

def category_for(title):
    text = title.lower()
    if any(term in text for term in ['محام', 'مرافعات', 'دعوى', 'خصومة', 'استئناف']):
        return 'المحاماة والمرافعات'
    if any(term in text for term in ['قضاء', 'قضائي', 'محكمة', 'محاكم', 'قاضي', 'قضاة', 'عدالة']):
        return 'القضاء'
    if any(term in text for term in ['جنائي', 'جزائي', 'جريمة', 'جرائم', 'عقوبة']):
        return 'الأنظمة الجزائية'
    if any(term in text for term in ['تجاري', 'منافسة', 'مدني', 'عقار', 'ملكية', 'عقود', 'عقد']):
        return 'القانون التجاري والمدني'
    return 'الأنظمة والقوانين'

with ANALYSIS.open(encoding='utf-8') as file:
    analysis = json.load(file)
with ITEMS.open(encoding='utf-8') as file:
    existing_items = json.load(file)

existing_links = {canonical(item.get('link_direct', '')) for item in existing_items if item.get('link_direct')}
seen = set()
candidates = []

for message in analysis.get('candidates', []):
    text = message.get('text', '')
    title = title_from_post(text)
    if len(title) < 10 or len(title) > 180:
        continue
    hits = [term for term in TITLE_TERMS if term in title.lower()]
    excluded = [term for term in OUT_OF_SCOPE if term in title.lower()]
    if not hits or excluded:
        continue
    for raw_url in message.get('urls', []):
        url = raw_url.rstrip('.,;،؛')
        parsed = urlparse(url)
        if parsed.netloc.lower() not in ALLOWED_HOSTS or '/web/doghaither/' not in parsed.path:
            continue
        key = canonical(url)
        if key in seen or key in existing_links:
            continue
        seen.add(key)
        candidates.append({
            'source_message_id': message.get('message_id'),
            'title': title,
            'author': 'د. عبدالعزيز بن سعد الدغيثر',
            'link_direct': url,
            'category': category_for(title),
            'material_type': 'بحث' if any(word in title for word in ['بحث', 'دراسة']) else 'مقال',
            'file_type': 'رابط',
            'match_terms': hits,
        })

with OUTPUT.open('w', encoding='utf-8') as file:
    json.dump(candidates, file, ensure_ascii=False, indent=2)

print(f'مرشحون مستوفون للشروط: {len(candidates)}')
for item in candidates:
    print(f"[{item['source_message_id']}] {item['category']} | {item['title']} | {item['link_direct']}")
