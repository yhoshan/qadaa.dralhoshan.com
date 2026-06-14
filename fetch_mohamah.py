"""
استخراج مجلة المحاماة وجميع المواد القانونية المفيدة من أرشيف الإنترنت
"""
import json, urllib.request, urllib.parse, time, re

def normalize(text):
    text = re.sub(r'[أإآا]', 'ا', text)
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = text.replace('ة', 'ه').replace('ى', 'ي')
    return text.lower().strip()

# كلمات سلبية قاطعة
NEGATIVE = [
    # روائيون وأدباء وكتّاب سياسيون تظهر أعمالهم بسبب الكلمات المشتركة
    'ثروت أباظة', 'نجيب محفوظ', 'يوسف إدريس', 'إحسان عبد القدوس',
    'طه حسين', 'توفيق الحكيم', 'عباس محمود العقاد',
    'بدر الدين السباعي', 'المرحلة الانتقالية',
    'فرج فودة', 'العلمانية', 'الدولة العلمانية', 'قبل السقوط',
    'زواج المتعة', 'الحقيقة الغائبة', 'النذير',
    'الأعمال الكاملة', 'الملعوب',
    # أسماء مشبوهة
    'هارب من الأيام', 'جدول بلا ماء', 'الضباب', 'نيام بلا مضاجع',
    'أمواج ولا شاطئ', 'رؤوس في السماء', 'خيوط واهية',
    'قصر النيل', 'ذهب خيوط', 'طائر في العنق',
    # تاريخ وجغرافيا
    'تاريخ اليونان', 'تاريخ روما', 'علم الاجتماع', 'علم النفس',
    'الكيمياء', 'الفيزياء', 'الرياضيات', 'الهندسة', 'الطب',
    'الأدب', 'الشعر', 'الرواية', 'المسرح', 'القصة',
    'التفسير', 'الحديث النبوي', 'السيرة النبوية', 'العقيدة',
    'الصلاة', 'الزكاة', 'الصيام', 'الحج',
    'موسوعة مقروءة', 'مكتبة شاملة', 'مجموعة كتب', 'كتب صيغة',
    'قضاء الله', 'قضاء الحاجة', 'قضاء وقدر',
    'قضية فلسطين', 'قضية الجزائر',
    'الاقتصاد', 'المحاسبة', 'التسويق',
    'الجغرافيا', 'الفلك', 'البيئة',
    'اللغة العربية', 'النحو', 'الصرف', 'البلاغة',
    'التربية', 'التعليم',
    'السياسة الدولية', 'العلاقات الدولية',
    'الفلسطينية', 'الصهيونية',
    'txt', 'ويب اتش', 'وورد ورد',
    'كفر وإيمان', 'التكفير', 'الجهاد والقتال',
    'حزب التحرير', 'الإخوان المسلمين',
]

# كلمات إيجابية يجب أن تكون في العنوان
POSITIVE = [
    'محاماة', 'محامي', 'محامون', 'المحامين', 'نقابة المحامين',
    'مجلة المحاماة', 'مجلة المحامون', 'مجلة المحامين',
    'قانون', 'قانوني', 'قانونية', 'القانون',
    'قضاء', 'قضائي', 'قضائية', 'محكمة', 'محاكم',
    'جناية', 'جنايات', 'جنائي', 'عقوبة', 'عقوبات',
    'تحكيم', 'مرافعة', 'دعوى', 'إثبات',
    'نظام الاجراءات', 'نظام القضاء', 'التشريع',
    'الفقه القضائي', 'أحكام القضاء',
    'الجريمة والعقوبة', 'جرائم',
    'الإجراءات الجزائية', 'الإجراءات الجنائية',
    'قانون الأسرة', 'الأحوال الشخصية',
    'القضاء الإداري', 'القضاء الشرعي',
    'الحكم القضائي', 'الأحكام القضائية',
    'الوساطة القضائية', 'الصلح القضائي',
    'نظام الأحوال', 'نظام العمل', 'نظام الشركات',
    'الجزاء', 'العقاب', 'الحبس', 'السجن',
    'القصاص والدية', 'الدية',
    'مجلة القانون', 'مجلة الحقوق', 'مجلة الشريعة والقانون',
    'مجلة القضاء', 'مجلة العدل',
    'حقوق الإنسان', 'حقوق المتهم',
    'الوكالة القانونية', 'الدفاع القانوني',
]

def has_negative(title):
    norm = normalize(title)
    return any(normalize(n) in norm for n in NEGATIVE)

def has_positive(title):
    norm = normalize(title)
    return any(normalize(p) in norm for p in POSITIVE)

def classify(title):
    norm = normalize(title)
    if any(w in norm for w in ['محاماه', 'محامي', 'محامون', 'محامين', 'نقابه']):
        return 'المحاماة والتحكيم', 'محاماة'
    elif any(w in norm for w in ['جناي', 'حدود', 'عقوبه', 'جريمه', 'قانون جنائي']):
        return 'الجنايات والحدود', 'قضاء'
    elif any(w in norm for w in ['قضاء اداري', 'ديوان مظالم', 'مجلس دوله']):
        return 'القضاء الإداري', 'أنظمة'
    elif any(w in norm for w in ['احوال شخصيه', 'اسره', 'طلاق', 'نفقه', 'ميراث']):
        return 'الأحوال الشخصية', 'قضاء'
    elif any(w in norm for w in ['تحكيم', 'وساطه']):
        return 'التحكيم والوساطة', 'محاماة'
    elif any(w in norm for w in ['نظام', 'تشريع', 'لائحه']):
        return 'الأنظمة والتشريعات', 'أنظمة'
    elif any(w in norm for w in ['مجله', 'دوريه']):
        return 'المجلات القانونية', 'محاماة'
    else:
        return 'القضاء الشرعي', 'قضاء'

# استعلامات البحث
QUERIES = [
    'مجلة المحاماة',
    'مجلة المحامون',
    'مجلة المحامين',
    'نقابة المحامين',
    'المحامون مجلة',
    'مجلة القانون',
    'مجلة الحقوق',
    'مجلة الشريعة والقانون',
    'مجلة القضاء',
    'مجلة العدل',
    'مجلة الأحكام',
    'مجلة التشريع والقضاء',
]

all_docs = {}
for query in QUERIES:
    params = urllib.parse.urlencode({
        'q': f'{query} AND mediatype:texts',
        'output': 'json',
        'rows': 200,
        'start': 0,
        'fl': 'identifier,title,creator,date,subject',
    })
    url = f'https://archive.org/advancedsearch.php?{params}'
    try:
        req = urllib.request.urlopen(url, timeout=15)
        data = json.loads(req.read())
        docs = data['response']['docs']
        total = data['response']['numFound']
        for doc in docs:
            iid = doc.get('identifier', '')
            if iid:
                all_docs[iid] = doc
        print(f'{query}: {total} نتيجة، جُلب {len(docs)} | الإجمالي: {len(all_docs)}')
    except Exception as e:
        print(f'خطأ في {query}: {e}')
    time.sleep(0.4)

print(f'\nإجمالي قبل التصفية: {len(all_docs)}')

# تصفية
filtered = []
for iid, doc in all_docs.items():
    title = doc.get('title', '').strip()
    if not title or len(title) < 4:
        continue
    if has_negative(title):
        continue
    # للمجلات نتساهل قليلاً — يكفي عدم وجود كلمة سلبية
    # لكن للكتب نشترط كلمة إيجابية
    arabic_chars = sum(1 for c in title if '\u0600' <= c <= '\u06FF')
    if arabic_chars < len(title) * 0.25:
        continue

    creator = doc.get('creator', '')
    if isinstance(creator, list):
        creator = creator[0] if creator else ''
    date = doc.get('date', '')
    if isinstance(date, list):
        date = date[0] if date else ''

    category, section = classify(title)

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
        'material_type': 'مجلة' if 'مجل' in normalize(title) else 'كتاب',
        'file_type': 'PDF',
        'file_size': '',
        'pages_count': '',
        'is_featured': False,
        'download_links_count': 1,
    }
    filtered.append(item)

print(f'بعد التصفية: {len(filtered)} مادة')

# عرض عينة
print('\nعينة:')
for item in filtered[:20]:
    print(f'  [{item["category"]}] {item["title"][:70]}')

with open('/home/ubuntu/makanez-qadaa/mohamah_items.json', 'w', encoding='utf-8') as f:
    json.dump(filtered, f, ensure_ascii=False, indent=2)

print(f'\nتم حفظ {len(filtered)} مادة في mohamah_items.json')
