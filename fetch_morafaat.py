"""
استخراج مواد المرافعات والإجراءات القضائية من أرشيف الإنترنت
"""
import json, urllib.request, urllib.parse, time, re

def normalize(text):
    text = re.sub(r'[أإآا]', 'ا', text)
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = text.replace('ة', 'ه').replace('ى', 'ي')
    return text.lower().strip()

NEGATIVE = [
    # أدباء وروائيون
    'ثروت أباظة', 'نجيب محفوظ', 'يوسف إدريس', 'إحسان عبد القدوس',
    'طه حسين', 'توفيق الحكيم', 'فرج فودة', 'العلمانية',
    # عناوين أدبية مشبوهة
    'هارب من الأيام', 'جدول بلا ماء', 'الضباب', 'نيام بلا مضاجع',
    'أمواج ولا شاطئ', 'رؤوس في السماء', 'خيوط واهية',
    'قصر النيل', 'طائر في العنق', 'قبل السقوط', 'الملعوب',
    # مواضيع غير ذات صلة
    'تاريخ اليونان', 'تاريخ روما', 'علم الاجتماع', 'علم النفس',
    'الكيمياء', 'الفيزياء', 'الرياضيات', 'الهندسة', 'الطب',
    'الأدب', 'الشعر', 'الرواية', 'المسرح', 'القصة',
    'التفسير', 'الحديث النبوي', 'السيرة النبوية', 'العقيدة',
    'الصلاة', 'الزكاة', 'الصيام', 'الحج',
    'موسوعة مقروءة', 'مكتبة شاملة', 'مجموعة كتب',
    'قضاء الله', 'قضاء الحاجة', 'قضاء وقدر',
    'قضية فلسطين', 'قضية الجزائر',
    'الاقتصاد', 'المحاسبة', 'التسويق',
    'الجغرافيا', 'الفلك', 'البيئة',
    'اللغة العربية', 'النحو', 'الصرف', 'البلاغة',
    'التربية', 'التعليم',
    'السياسة الدولية', 'العلاقات الدولية',
    'الفلسطينية', 'الصهيونية',
    'كفر وإيمان', 'التكفير',
    'حزب التحرير', 'الإخوان المسلمين',
    'زواج المتعة', 'الحقيقة الغائبة',
    'الأعمال الكاملة',
]

POSITIVE = [
    'مرافعات', 'مرافعة', 'المرافعات',
    'إجراءات جزائية', 'إجراءات جنائية', 'إجراءات مدنية',
    'الإجراءات القضائية', 'الإجراءات الجنائية',
    'قانون المرافعات', 'قانون الإجراءات',
    'التقاضي', 'الدعوى', 'الدعاوى',
    'الخصومة القضائية', 'الخصومة',
    'التحقيق الجنائي', 'التحقيق القضائي',
    'الاستئناف', 'النقض', 'التمييز',
    'الحكم القضائي', 'الأحكام القضائية',
    'التنفيذ القضائي', 'تنفيذ الأحكام',
    'الإثبات القضائي', 'إثبات',
    'الشهادة والشهود', 'الشهادة',
    'قانون الإثبات', 'قانون الأدلة',
    'المحاكمة', 'محاكمة',
    'الاختصاص القضائي',
    'القضاء المدني', 'القضاء الجنائي',
    'مجلة المرافعات', 'قانون قضائي',
]

def has_negative(title):
    norm = normalize(title)
    return any(normalize(n) in norm for n in NEGATIVE)

def has_positive(title):
    norm = normalize(title)
    return any(normalize(p) in norm for p in POSITIVE)

def classify(title):
    norm = normalize(title)
    if any(w in norm for w in ['مرافعه', 'تقاضي', 'دعوى', 'دعاوى', 'خصومه', 'استئناف', 'نقض', 'تمييز']):
        return 'المحاكم والمرافعات', 'قضاء'
    elif any(w in norm for w in ['اجراءات جزائيه', 'اجراءات جنائيه', 'تحقيق جنائي']):
        return 'الإجراءات القضائية', 'قضاء'
    elif any(w in norm for w in ['اثبات', 'شهاده', 'شهود', 'اقرار', 'يمين']):
        return 'الإثبات والشهادة', 'قضاء'
    elif any(w in norm for w in ['تنفيذ', 'حكم قضائي', 'احكام قضائيه']):
        return 'المبادئ والقرارات القضائية', 'قضاء'
    else:
        return 'المحاكم والمرافعات', 'قضاء'

QUERIES = [
    'المرافعات',
    'قانون المرافعات',
    'الإجراءات الجنائية',
    'الإجراءات الجزائية',
    'الإجراءات المدنية',
    'قانون الإثبات',
    'التقاضي',
    'الدعوى القضائية',
    'الاستئناف القضائي',
    'التحقيق الجنائي',
    'تنفيذ الأحكام',
    'المحاكمة الجنائية',
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
    print(f'{query}: الإجمالي حتى الآن: {len(all_docs)}')

print(f'\nإجمالي قبل التصفية: {len(all_docs)}')

# تصفية صارمة
filtered = []
for iid, doc in all_docs.items():
    title = doc.get('title', '').strip()
    if not title or len(title) < 4:
        continue
    if has_negative(title):
        continue
    if not has_positive(title):
        continue
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
        'material_type': 'كتاب',
        'file_type': 'PDF',
        'file_size': '',
        'pages_count': '',
        'is_featured': False,
        'download_links_count': 1,
    }
    filtered.append(item)

print(f'بعد التصفية: {len(filtered)} مادة')
print('\nعينة:')
for item in filtered[:20]:
    print(f'  [{item["category"]}] {item["title"][:70]}')

with open('/home/ubuntu/makanez-qadaa/morafaat_items.json', 'w', encoding='utf-8') as f:
    json.dump(filtered, f, ensure_ascii=False, indent=2)
print(f'\nتم حفظ {len(filtered)} مادة في morafaat_items.json')
