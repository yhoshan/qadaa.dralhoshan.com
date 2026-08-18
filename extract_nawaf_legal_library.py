import json
import re
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import quote, unquote, urljoin, urlparse, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

PROJECT = Path('/home/ubuntu/makanez-qadaa')
SOURCE_FILE = Path('/home/ubuntu/upload/pasted_file_AMdIwg_deepseek_json_20260818_09965d.json')
ITEMS_FILE = PROJECT / 'items.json'
OUTPUT = PROJECT / 'nawaf_legal_library_candidates.json'

SOURCE_NAME = 'المكتبة القانونية — موقع نواف للأنظمة والقضاء'
SOURCE_ROOT = 'https://nawaf-law.com.sa/المكتبة-القانونية/'
MEDIA_EXTENSIONS = ('.pdf', '.doc', '.docx', '.zip', '.rar')

def canonical_link(url):
    parsed = urlparse(url)
    return f'{parsed.scheme.lower()}://{parsed.netloc.lower()}{parsed.path.rstrip("/")}'

def normalize(text):
    text = unicodedata.normalize('NFKC', text or '')
    text = unquote(text)
    text = re.sub(r'\.(pdf|docx?|zip|rar)$', '', text, flags=re.I)
    text = re.sub(r'[\W_]+', ' ', text, flags=re.UNICODE)
    text = re.sub(r'[أإآٱ]', 'ا', text)
    text = text.replace('ى', 'ي').replace('ة', 'ه')
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text

def url_label(url):
    path = unquote(urlparse(url).path)
    name = path.rsplit('/', 1)[-1]
    return normalize(name)

def text_similarity(left, right):
    return SequenceMatcher(None, normalize(left), normalize(right)).ratio()

def fetch_links(category):
    page_url = category['page_url']
    parts = urlsplit(page_url)
    safe_url = urlunsplit((parts.scheme, parts.netloc, quote(parts.path), quote(parts.query, safe='=&'), parts.fragment))
    request = Request(safe_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(request, timeout=20) as response:
        html = response.read().decode('utf-8', errors='ignore')
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for tag in soup.find_all('a', href=True):
        href = urljoin(page_url, tag['href']).strip()
        path = urlparse(href).path.lower()
        if path.endswith(MEDIA_EXTENSIONS) and '/wp-content/uploads/' in path and not path.endswith('/profile-ar.pdf'):
            links.append(href)
    return category['name'], sorted(set(links))

def category_mapping(name):
    if name in {'قضاء التنفيذ', 'القضاء الإداري – ديوان المظالم', 'القضاء التجاري', 'القضاء العمالي', 'قضاء الأحوال الشخصية', 'القضاء الجزائي', 'القضاء العام', 'مجموعات الأحكام القضائية', 'التسبيبات القضائية', 'منازعات اللجان شبه القضائية'}:
        return 'القضاء الشرعي'
    if name in {'التعاميم والقرارات', 'الأنظمة'}:
        return 'الأنظمة والتشريعات'
    if name == 'النماذج والقوالب القضائية':
        return 'المحاكم والمرافعات'
    return 'الأنظمة والتشريعات'

def material_mapping(name, title):
    if 'حقيبة' in title or 'دورة' in title:
        return 'حقيبة تدريبية'
    if title.startswith('نظام ') or title.startswith('اللائحة') or 'تعميم' in title or title.startswith('قرار'):
        return 'نظام'
    if 'مذكرة' in title:
        return 'مذكرة'
    if 'مجموعة الأحكام' in title or 'السوابق' in title or 'المبادئ' in title or 'تسبيبات' in title:
        return 'أحكام قضائية'
    if 'نموذج' in title or 'قالب' in title:
        return 'نموذج'
    if 'دراسة' in title or 'بحث' in title:
        return 'بحث'
    return 'كتاب'

with SOURCE_FILE.open(encoding='utf-8') as f:
    source_data = json.load(f)
with ITEMS_FILE.open(encoding='utf-8') as f:
    existing_items = json.load(f)

existing_links = {canonical_link(item.get('link_direct', '')) for item in existing_items if item.get('link_direct')}
existing_titles = [normalize(item.get('title', '')) for item in existing_items if item.get('title')]

category_links = {}
with ThreadPoolExecutor(max_workers=6) as executor:
    futures = {executor.submit(fetch_links, category): category['name'] for category in source_data['categories']}
    for future in as_completed(futures):
        category_name = futures[future]
        try:
            name, links = future.result()
            category_links[name] = links
        except Exception as error:
            category_links[category_name] = []
            print(f'تعذر فحص {category_name}: {error}')

candidates = []
unmatched = []
skipped_duplicates = []
used_links = set()

for category in source_data['categories']:
    category_name = category['name']
    links = category_links.get(category_name, [])
    labels = [(link, url_label(link)) for link in links]
    for book in category['books']:
        title = re.sub(r'\s+', ' ', (book.get('title') or '')).strip()
        author = (book.get('author') or '').strip()
        title_normalized = normalize(title)
        scores = [(text_similarity(title, label), link) for link, label in labels if link not in used_links]
        score, matched_link = max(scores, default=(0, ''))

        # Keep only high-confidence title/link matches so no guessed link enters the index.
        if score < 0.62:
            unmatched.append({'category': category_name, 'title': title, 'author': author, 'best_score': round(score, 3)})
            continue
        used_links.add(matched_link)
        duplicate_title = max((SequenceMatcher(None, title_normalized, old_title).ratio() for old_title in existing_titles), default=0)
        if canonical_link(matched_link) in existing_links or duplicate_title >= 0.93:
            skipped_duplicates.append({'category': category_name, 'title': title, 'author': author, 'link': matched_link, 'title_similarity': round(duplicate_title, 3)})
            continue
        candidates.append({
            'title': title,
            'author': author,
            'category': category_mapping(category_name),
            'source_section': category_name,
            'source': SOURCE_NAME,
            'source_url': SOURCE_ROOT,
            'link_direct': matched_link,
            'material_type': material_mapping(category_name, title),
            'file_type': urlparse(matched_link).path.rsplit('.', 1)[-1].upper(),
            'match_score': round(score, 3),
        })

result = {
    'source': SOURCE_NAME,
    'source_url': SOURCE_ROOT,
    'source_category_count': len(source_data['categories']),
    'source_title_count': sum(len(category['books']) for category in source_data['categories']),
    'links_found_by_category': {name: len(links) for name, links in category_links.items()},
    'candidate_count': len(candidates),
    'duplicate_count': len(skipped_duplicates),
    'unmatched_count': len(unmatched),
    'candidates': candidates,
    'duplicates': skipped_duplicates,
    'unmatched': unmatched,
}
with OUTPUT.open('w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(json.dumps({
    'source_titles': result['source_title_count'],
    'direct_links_found': sum(result['links_found_by_category'].values()),
    'candidates': result['candidate_count'],
    'duplicates': result['duplicate_count'],
    'unmatched': result['unmatched_count'],
    'output': str(OUTPUT),
}, ensure_ascii=False, indent=2))
