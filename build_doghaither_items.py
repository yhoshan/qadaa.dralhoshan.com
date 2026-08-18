import html
import json
import re
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ANALYSIS = Path('/home/ubuntu/makanez-qadaa/doghaither_channel_analysis.json')
ITEMS = Path('/home/ubuntu/makanez-qadaa/items.json')
OUTPUT = Path('/home/ubuntu/makanez-qadaa/doghaither_legal_candidates.json')

ALLOWED_HOSTS = {'www.alukah.net', 'alukah.net'}
IN_SCOPE = [
    'قضاء', 'قضائي', 'محكمة', 'محاكم', 'قاضي', 'قضاة', 'عدالة', 'دعوى',
    'دعاوى', 'تحكيم', 'محام', 'مرافعات', 'تنفيذ', 'استئناف', 'خصومة',
    'نظام', 'أنظمة', 'نظامي', 'لائحة', 'لوائح', 'قانون', 'قانوني',
    'تجاري', 'مدني', 'جنائي', 'جزائي', 'إداري', 'دستوري', 'منافسة',
    'حقوق', 'حق ', 'عقد', 'عقود', 'إثبات', 'بينات', 'عقار', 'ملكية',
    'تعويض', 'مسؤولية', 'جريمة', 'جرائم', 'عقوبة', 'عقوبات', 'وقف',
    'وصية', 'مواريث', 'نفقة', 'طلاق', 'حضانة', 'زواج', 'أسرة'
]
OUT_OF_SCOPE = [
    'التوحيد', 'العقيدة', 'التفسير', 'القرآن', 'القران', 'الحديث',
    'السيرة', 'رمضان', 'الصلاة', 'الصيام', 'الحج', 'الزكاة', 'الأذكار',
    'الدعاء', 'الرقية', 'تجويد', 'قراءات', 'اللغة العربية', 'الشعر'
]

class PageMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ''
        self.og_title = ''
        self.description = ''
        self._in_title = False
        self._title_parts = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == 'title':
            self._in_title = True
        if tag == 'meta':
            key = (data.get('property') or data.get('name') or '').lower()
            content = data.get('content', '')
            if key == 'og:title':
                self.og_title = content
            if key in {'description', 'og:description'} and not self.description:
                self.description = content

    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self._title_parts.append(data)

    def finish(self):
        self.title = ''.join(self._title_parts).strip()

def normalize(value):
    value = html.unescape(value or '')
    value = re.sub(r'\s+', ' ', value)
    return value.strip()

def flatten_title(text):
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'^د\.?\s*عبدالعزيز\s*الدغيثر.*?(?:محامي\.?\s*:?)?', '', text, flags=re.I | re.S)
    text = re.sub(r'\(PDF\)', '', text, flags=re.I)
    text = normalize(text)
    return text.split('\n')[0].strip(' -–:')

def canonical(url):
    parsed = urlparse(url)
    return f'{parsed.scheme.lower()}://{parsed.netloc.lower()}{parsed.path.rstrip("/")}/'

def fetch_page(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            content = response.read(900_000).decode('utf-8', errors='ignore')
            final_url = response.geturl()
        parser = PageMetadata()
        parser.feed(content)
        parser.finish()
        return {
            'url': final_url,
            'title': normalize(parser.og_title or parser.title),
            'description': normalize(parser.description),
        }
    except Exception as error:
        return {'url': url, 'title': '', 'description': '', 'error': str(error)}

def category_for(text):
    if any(term in text for term in ['محام', 'مرافعات', 'دعوى', 'خصومة', 'استئناف']):
        return 'المحاماة والمرافعات'
    if any(term in text for term in ['قضاء', 'قضائي', 'محكمة', 'محاكم', 'قاضي', 'قضاة', 'عدالة']):
        return 'القضاء'
    if any(term in text for term in ['عقود', 'عقد', 'تجاري', 'منافسة', 'مدني', 'عقار', 'ملكية']):
        return 'القانون التجاري والمدني'
    if any(term in text for term in ['جنائي', 'جزائي', 'جريمة', 'جرائم', 'عقوبة']):
        return 'الأنظمة الجزائية'
    return 'الأنظمة والقوانين'

with ANALYSIS.open(encoding='utf-8') as file:
    analysis = json.load(file)
with ITEMS.open(encoding='utf-8') as file:
    existing_items = json.load(file)

existing_links = {canonical(item.get('link_direct', '')) for item in existing_items if item.get('link_direct')}
seen = set()
candidates = []

for message in analysis.get('candidates', []):
    for raw_url in message.get('urls', []):
        url = raw_url.rstrip('.,;،؛')
        parsed = urlparse(url)
        if parsed.netloc.lower() not in ALLOWED_HOSTS:
            continue
        if '/web/doghaither/' not in parsed.path:
            continue
        key = canonical(url)
        if key in seen or key in existing_links:
            continue
        seen.add(key)

        metadata = fetch_page(url)
        source_text = f"{message.get('text', '')} {metadata.get('title', '')} {metadata.get('description', '')}".lower()
        in_scope_hits = [term for term in IN_SCOPE if term in source_text]
        out_scope_hits = [term for term in OUT_OF_SCOPE if term in source_text]
        title = metadata.get('title') or flatten_title(message.get('text', ''))
        title = re.sub(r'\s*[-|]\s*(?:شبكة الألوكة|موقع الألوكة).*$', '', title).strip()
        
        if not title or not in_scope_hits or len(out_scope_hits) >= len(in_scope_hits):
            continue
        if len(title) < 8:
            continue

        candidates.append({
            'source_message_id': message.get('message_id'),
            'title': title,
            'author': 'د. عبدالعزيز بن سعد الدغيثر',
            'link_direct': metadata.get('url', url),
            'category': category_for(source_text),
            'material_type': 'بحث' if any(word in source_text for word in ['بحث', 'دراسة']) else 'مقال',
            'file_type': 'رابط',
            'match_terms': in_scope_hits,
            'page_description': metadata.get('description', ''),
        })
        time.sleep(0.2)

with OUTPUT.open('w', encoding='utf-8') as file:
    json.dump(candidates, file, ensure_ascii=False, indent=2)

print(f'مرشحون مستوفون للشروط: {len(candidates)}')
for item in candidates:
    print(f"[{item['source_message_id']}] {item['category']} | {item['title']} | {item['link_direct']}")
