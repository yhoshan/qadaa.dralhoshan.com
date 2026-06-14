"""
استخراج مواد التحكيم والقانون الدولي من أرشيف الإنترنت
"""
import json, urllib.request, urllib.parse, time, re

def normalize(text):
    text = re.sub(r'[أإآا]', 'ا', text)
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = text.replace('ة', 'ه').replace('ى', 'ي')
    return text.lower().strip()

DIRTY = [
    'كلمة السر', 'كمبوتة', 'اقرا اونلاين', 'اقرأ اونلاين',
    'file download', 'pdf file', 'كتاب pdf', 'book pdf',
    'كتاب اقرا', 'Book ', 'الانضمة السعودية صيغة وورد',
    'ثروت أباظة', 'نجيب محفوظ', 'يوسف إدريس', 'إحسان عبد القدوس',
    'طه حسين', 'توفيق الحكيم', 'فرج فودة',
    'تاريخ اليونان', 'تاريخ روما', 'علم الاجتماع', 'علم النفس',
    'الكيمياء', 'الفيزياء', 'الرياضيات', 'الهندسة',
    'الأدب', 'الشعر', 'الرواية', 'المسرح', 'القصة',
    'التفسير', 'الحديث النبوي', 'السيرة النبوية', 'العقيدة',
    'الصلاة', 'الزكاة', 'الصيام', 'الحج',
    'موسوعة مقروءة', 'مكتبة شاملة', 'مجموعة كتب',
    'قضاء الله', 'قضاء الحاجة', 'قضاء وقدر',
    'قضية فلسطين', 'قضية الجزائر', 'قضية فلسطينية',
    'الاقتصاد السياسي', 'المحاسبة', 'التسويق',
    'الجغرافيا', 'الفلك', 'البيئة',
    'اللغة العربية', 'النحو', 'الصرف', 'البلاغة',
    'التربية', 'التعليم',
    'كفر وإيمان', 'التكفير',
    'حزب التحرير', 'الإخوان المسلمين',
    'الأعمال الكاملة',
    'التحكيم الرياضي الدولي',  # رياضة
    'التحكيم في كرة', 'التحكيم الكروي',
    'حكام كرة', 'حكم المباراة',
]

NEGATIVE_STRICT = [
    'رياضة', 'كرة القدم', 'كرة', 'ملعب', 'حكام الملاعب',
    'السياسة الدولية للطاقة', 'البترول السياسي',
    'الاستعمار', 'الاستقلال السياسي',
    'الجغرافيا السياسية',
]

POSITIVE_TAHKEEM = [
    'التحكيم التجاري', 'التحكيم الدولي', 'التحكيم في المنازعات',
    'التحكيم الاستثماري', 'التحكيم الإلكتروني', 'التحكيم البحري',
    'التحكيم والوساطة', 'التحكيم في العقود', 'التحكيم في الفقه',
    'نظام التحكيم', 'قانون التحكيم', 'هيئة التحكيم',
    'اتفاق التحكيم', 'شرط التحكيم', 'محكم', 'محكمون',
    'الوساطة والتوفيق', 'الوساطة في النزاعات',
    'التسوية الودية', 'تسوية النزاعات',
    'ICSID', 'ICC arbitration', 'arbitration',
]

POSITIVE_INTL = [
    'القانون الدولي', 'القانون الدولي الخاص', 'القانون الدولي العام',
    'القانون الدولي الإنساني', 'القانون الدولي لحقوق الإنسان',
    'القانون الدولي الجنائي', 'المحكمة الجنائية الدولية',
    'محكمة العدل الدولية', 'القضاء الدولي',
    'الاتفاقيات الدولية', 'المعاهدات الدولية',
    'التعاون القضائي الدولي', 'تسليم المجرمين',
    'حقوق الإنسان', 'القانون الإنساني الدولي',
    'اتفاقية جنيف', 'اتفاقية نيويورك',
    'القانون البحري الدولي', 'القانون الجوي الدولي',
    'القانون التجاري الدولي', 'قانون التجارة الدولية',
    'النزاعات الدولية', 'فض النزاعات الدولية',
    'الاستثمار الأجنبي', 'حماية الاستثمار',
    'التحكيم الاستثماري الدولي',
]

def is_dirty(title):
    norm = normalize(title)
    for p in DIRTY:
        if normalize(p) in norm:
            return True
    for p in NEGATIVE_STRICT:
        if normalize(p) in norm:
            return True
    if re.match(r'^\d{6}\s*[-_]', title.strip()):
        return True
    return False

def has_positive(title, pos_list):
    norm = normalize(title)
    return any(normalize(p) in norm for p in pos_list)

def classify(title):
    norm = normalize(title)
    if any(w in norm for w in ['تحكيم', 'وساطه', 'توفيق', 'تسويه وديه', 'نزاعات']):
        return 'التحكيم والوساطة', 'محاماة'
    elif any(w in norm for w in ['قانون دولي خاص', 'تنازع قوانين', 'تنازع اختصاص']):
        return 'الأنظمة والتشريعات', 'أنظمة'
    elif any(w in norm for w in ['محكمه جنائيه دوليه', 'قضاء دولي', 'جرائم دوليه']):
        return 'الجنايات والحدود', 'قضاء'
    elif any(w in norm for w in ['حقوق الانسان', 'قانون انساني', 'اتفاقيه جنيف']):
        return 'الأنظمة والتشريعات', 'أنظمة'
    elif any(w in norm for w in ['استثمار', 'تجاره دوليه', 'قانون تجاري دولي']):
        return 'الأنظمة والتشريعات', 'أنظمة'
    else:
        return 'الأنظمة والتشريعات', 'أنظمة'

QUERIES = [
    # التحكيم
    'التحكيم التجاري الدولي',
    'التحكيم في المنازعات',
    'نظام التحكيم',
    'قانون التحكيم',
    'التحكيم والوساطة',
    'الوساطة في النزاعات',
    'التحكيم الاستثماري',
    'التحكيم الإلكتروني',
    'اتفاق التحكيم',
    # القانون الدولي
    'القانون الدولي الخاص',
    'القانون الدولي العام',
    'القانون الدولي الإنساني',
    'محكمة العدل الدولية',
    'القانون الدولي الجنائي',
    'التعاون القضائي الدولي',
    'حقوق الإنسان القانون الدولي',
    'القانون التجاري الدولي',
    'الاستثمار الأجنبي القانون',
    'المعاهدات الدولية',
    'تسليم المجرمين',
]

all_docs = {}
for query in QUERIES:
    for mediatype in ['texts', 'data']:
        params = urllib.parse.urlencode({
            'q': f'{query} AND mediatype:{mediatype}',
            'output': 'json',
            'rows': 150,
            'start': 0,
            'fl': 'identifier,title,creator,date,subject',
        })
        url = f'https://archive.org/advancedsearch.php?{params}'
        try:
            req = urllib.request.urlopen(url, timeout=15)
            data = json.loads(req.read())
            docs = data['response']['docs']
            for doc in docs:
                iid = doc.get('identifier', '')
                if iid:
                    all_docs[iid] = doc
        except Exception as e:
            print(f'خطأ: {e}')
        time.sleep(0.3)
    print(f'{query}: {len(all_docs)} إجمالي')

print(f'\nقبل التصفية: {len(all_docs)}')

filtered = []
for iid, doc in all_docs.items():
    title = doc.get('title', '').strip()
    if not title or len(title) < 4:
        continue
    if is_dirty(title):
        continue
    if not (has_positive(title, POSITIVE_TAHKEEM) or has_positive(title, POSITIVE_INTL)):
        continue
    arabic_chars = sum(1 for c in title if '\u0600' <= c <= '\u06FF')
    if arabic_chars < len(title) * 0.15:
        continue

    creator = doc.get('creator', '')
    if isinstance(creator, list):
        creator = creator[0] if creator else ''
    date = doc.get('date', '')
    if isinstance(date, list):
        date = date[0] if date else ''

    category, section = classify(title)
    mat_type = 'مجلة' if any(w in normalize(title) for w in ['مجله', 'دوريه', 'نشره']) else 'كتاب'

    item = {
        'id': f'archive_{iid}',
        'title': title,
        'author': str(creator),
        'investigator': '',
        'publisher': 'أرشيف الإنترنت',
        'year': str(date)[:4] if date else '',
        'link_telegram': '',
        'link_drive': '',
        'link_direct': f'https://archive.org/download/{iid}/{iid}.pdf',
        'source': 'أرشيف الإنترنت',
        'category': category,
        'material_type': mat_type,
        'file_type': 'PDF',
        'file_size': '',
        'pages_count': '',
        'is_featured': False,
        'download_links_count': 1,
    }
    filtered.append(item)

print(f'بعد التصفية: {len(filtered)} مادة')
print('\nعينة:')
for item in filtered[:25]:
    print(f'  [{item["category"]}] {item["title"][:70]}')

with open('/home/ubuntu/makanez-qadaa/tahkeem_intl_items.json', 'w', encoding='utf-8') as f:
    json.dump(filtered, f, ensure_ascii=False, indent=2)
print(f'\nتم حفظ {len(filtered)} مادة')
