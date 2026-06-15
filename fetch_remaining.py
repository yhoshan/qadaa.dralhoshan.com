import json
import urllib.request
import urllib.parse
import time
import re

def fetch_archive(query, rows=300):
    """استخراج نتائج من أرشيف الإنترنت"""
    params = urllib.parse.urlencode({
        'q': f'({query}) AND language:(arabic OR ara)',
        'fl[]': ['identifier', 'title', 'creator', 'description', 'subject', 'date'],
        'rows': rows,
        'page': 1,
        'output': 'json',
        'mediatype': 'texts'
    })
    url = f'https://archive.org/advancedsearch.php?{params}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('response', {}).get('docs', [])
    except Exception as e:
        print(f'خطأ: {e}')
        return []

NEGATIVE_WORDS = [
    'رواية', 'شعر', 'ديوان', 'قصة', 'أدب', 'مسرحية', 'رياضة', 'كرة',
    'طبخ', 'وصفات', 'صحة', 'طب', 'هندسة', 'فيزياء', 'كيمياء',
    'رياضيات', 'جغرافيا', 'تاريخ طبيعي', 'علم النبات', 'حيوان',
    'لغة عربية', 'نحو', 'صرف', 'بلاغة', 'أدب عربي',
    'تفسير القرآن', 'علوم القرآن', 'حديث نبوي', 'سيرة نبوية',
    'عقيدة', 'توحيد', 'فلسفة', 'منطق', 'تصوف',
    'اقتصاد', 'تجارة', 'محاسبة', 'إدارة أعمال',
    'كمبيوتر', 'برمجة', 'تقنية', 'معلومات',
    'سياسة دولية', 'علاقات دولية', 'دبلوماسية',
]

BAD_TITLE_PATTERNS = [
    r'^\d+\s*$',
    r'^[a-z0-9_-]+$',
    r'كمبوتة|اقرا اونلاين|كلمة السر',
    r'Htm\s+أحاديث',
]

QUERIES = {
    'الأحوال الشخصية': [
        'الطلاق الفقه الإسلامي',
        'النفقة الزوجية الفقه',
        'الحضانة الأطفال الفقه',
        'الميراث والتركات الفقه',
        'الزواج والطلاق القانون',
        'الأحوال الشخصية القانون',
        'عقد الزواج الفقه الإسلامي',
    ],
    'الإثبات والشهادات': [
        'الإثبات القضائي الفقه',
        'الشهادة القضاء الإسلامي',
        'اليمين القضائية الفقه',
        'القرائن القضائية',
        'الإثبات الجنائي',
        'البينة والشهادة الفقه',
    ],
    'العقود والمعاملات': [
        'عقود المعاملات المالية الفقه',
        'البيع والشراء الفقه الإسلامي',
        'الإجارة والمقاولات الفقه',
        'الشركات التجارية القانون',
        'العقود التجارية القانون',
        'الملكية الفكرية القانون',
    ],
    'التشريع المقارن': [
        'الفقه الإسلامي والقانون الوضعي',
        'الشريعة الإسلامية والتشريع',
        'القانون المقارن الإسلامي',
        'الفقه الجنائي الإسلامي المقارن',
        'تطبيق الشريعة الإسلامية',
    ],
}

def is_relevant(title, description=""):
    if isinstance(title, list): title = " ".join(title)
    if isinstance(description, list): description = " ".join(description)
    title_str = str(title)
    title_lower = title_str.lower()

    # فحص الأنماط السيئة
    for pattern in BAD_TITLE_PATTERNS:
        if re.search(pattern, title_str.strip(), re.IGNORECASE):
            return False

    # استبعاد الكلمات السلبية
    for neg in NEGATIVE_WORDS:
        if neg in title_lower:
            return False

    # استبعاد القضاء والقدر
    if re.search(r'القضاء\s+والقدر|القدر\s+والقضاء|قضاء\s+الله\s+وقدر', title_lower):
        return False

    # استبعاد القضاء على بمعنى الإنهاء
    if re.search(r'القضاء\s+على\s+', title_lower):
        return False

    # يجب أن يكون العنوان عربياً بشكل معقول
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', title_str))
    if arabic_chars < 5:
        return False

    return True

def clean_title(title):
    if isinstance(title, list): title = title[0] if title else ""
    title = str(title)
    title = re.sub(r'\s*(Pdf|PDF|pdf)\s*(كتاب|File|file)?\s*\d*', '', title)
    title = re.sub(r'\s*(File|file)\s*(كتاب)?\s*\d*', '', title)
    title = re.sub(r'^\d+\s+', '', title)
    title = re.sub(r'\s+\[\d+\].*$', '', title)
    return title.strip()

def get_category(title, section):
    return section

# تحميل المواد الموجودة لتجنب التكرار
with open('items.json', encoding='utf-8') as f:
    existing_items = json.load(f)
existing_ids = {item['id'] for item in existing_items}

all_new = []
seen_ids = set()

for section, queries in QUERIES.items():
    print(f'\n📚 قسم: {section}')
    section_count = 0
    for query in queries:
        print(f'  🔍 {query}...')
        docs = fetch_archive(query, rows=200)
        time.sleep(1)
        for doc in docs:
            identifier = doc.get('identifier', '')
            if not identifier or identifier in seen_ids or identifier in existing_ids:
                continue
            title = doc.get('title', '')
            if not is_relevant(title):
                continue
            clean = clean_title(title)
            if len(clean) < 5:
                continue
            seen_ids.add(identifier)
            section_count += 1
            author = doc.get('creator', '')
            if isinstance(author, list): author = author[0] if author else ''
            all_new.append({
                'id': f'archive_{identifier}',
                'title': clean,
                'author': str(author),
                'investigator': '',
                'publisher': 'أرشيف الإنترنت',
                'year': str(doc.get('date', ''))[:4] if doc.get('date') else '',
                'link_telegram': '',
                'link_drive': '',
                'link_direct': f'https://archive.org/details/{identifier}',
                'source': 'أرشيف الإنترنت',
                'category': get_category(clean, section),
                'material_type': 'كتاب',
                'file_type': 'PDF',
                'file_size': '',
                'pages_count': '',
                'is_featured': False,
                'download_links_count': 1,
            })
    print(f'  → {section_count} مادة جديدة في هذا القسم')

print(f'\n✅ إجمالي المواد الجديدة: {len(all_new)}')

with open('archive_remaining.json', 'w', encoding='utf-8') as f:
    json.dump(all_new, f, ensure_ascii=False, indent=2)

print('تم الحفظ في archive_remaining.json')
