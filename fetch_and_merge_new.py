"""
1. تصفية مواد المرافعات (استبعاد العناوين المشوهة)
2. استخراج مجلة الحقوق من أرشيف الإنترنت
3. دمج الكل مع items.json
"""
import json, urllib.request, urllib.parse, time, re

def normalize(text):
    text = re.sub(r'[أإآا]', 'ا', text)
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = text.replace('ة', 'ه').replace('ى', 'ي')
    return text.lower().strip()

# كلمات تدل على عناوين مشوهة أو غير مرغوبة
DIRTY_PATTERNS = [
    'كلمة السر', 'كمبوتة', 'اقرا اونلاين', 'اقرأ اونلاين',
    'file download', 'pdf file', 'كتاب pdf', 'book pdf',
    'كتاب اقرا', 'كتاب Pdf', 'Book محاضرات',
    'الانضمة السعودية صيغة وورد',
    'ثروت أباظة', 'نجيب محفوظ', 'يوسف إدريس', 'إحسان عبد القدوس',
    'طه حسين', 'توفيق الحكيم', 'فرج فودة', 'العلمانية',
    'هارب من الأيام', 'جدول بلا ماء', 'الضباب', 'نيام بلا مضاجع',
    'أمواج ولا شاطئ', 'رؤوس في السماء', 'خيوط واهية',
    'قصر النيل', 'طائر في العنق', 'قبل السقوط', 'الملعوب',
    'تاريخ اليونان', 'تاريخ روما', 'علم الاجتماع', 'علم النفس',
    'الكيمياء', 'الفيزياء', 'الرياضيات', 'الهندسة',
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
    'كفر وإيمان', 'التكفير',
    'حزب التحرير', 'الإخوان المسلمين',
    'زواج المتعة', 'الحقيقة الغائبة',
    'الأعمال الكاملة',
]

def is_dirty(title):
    norm = normalize(title)
    for p in DIRTY_PATTERNS:
        if normalize(p) in norm:
            return True
    # عناوين رقمية مشبوهة مثل "046825 - تشريعات"
    if re.match(r'^\d{6}\s*-', title.strip()):
        return True
    return False

def classify_morafaat(title):
    norm = normalize(title)
    if any(w in norm for w in ['اثبات', 'شهاده', 'شهود', 'اقرار', 'يمين']):
        return 'الإثبات والشهادة'
    elif any(w in norm for w in ['اجراءات جزائيه', 'اجراءات جنائيه', 'تحقيق جنائي', 'تحقيق جزائي']):
        return 'الإجراءات القضائية'
    elif any(w in norm for w in ['تنفيذ', 'احكام قضائيه', 'حكم قضائي']):
        return 'المبادئ والقرارات القضائية'
    else:
        return 'المحاكم والمرافعات'

def classify_hoqooq(title):
    norm = normalize(title)
    if any(w in norm for w in ['محاماه', 'محامي', 'نقابه']):
        return 'المحاماة والتحكيم'
    elif any(w in norm for w in ['جناي', 'جنائي', 'عقوبه', 'جريمه']):
        return 'الجنايات والحدود'
    elif any(w in norm for w in ['نظام', 'تشريع', 'لائحه']):
        return 'الأنظمة والتشريعات'
    elif any(w in norm for w in ['مرافعه', 'اجراءات', 'دعوى']):
        return 'المحاكم والمرافعات'
    else:
        return 'المجلات القانونية'

# ===== الخطوة 1: تصفية مواد المرافعات =====
print("=== تصفية مواد المرافعات ===")
with open('/home/ubuntu/makanez-qadaa/morafaat_items.json', 'r', encoding='utf-8') as f:
    morafaat_raw = json.load(f)

morafaat_clean = []
for item in morafaat_raw:
    if not is_dirty(item['title']):
        item['category'] = classify_morafaat(item['title'])
        morafaat_clean.append(item)

print(f"قبل: {len(morafaat_raw)} | بعد: {len(morafaat_clean)}")

# ===== الخطوة 2: استخراج مجلة الحقوق =====
print("\n=== استخراج مجلة الحقوق ===")
HOQOOQ_QUERIES = [
    'مجلة الحقوق',
    'مجلة الحقوق الكويتية',
    'مجلة الحقوق والشريعة',
    'مجلة الحقوق والعلوم السياسية',
    'مجلة الحقوق والعلوم القانونية',
    'مجلة الحقوق المقارن',
    'مجلة القانون والاقتصاد',
    'مجلة الفكر القانوني',
    'مجلة البحوث القانونية',
    'مجلة الدراسات القانونية',
    'مجلة الشريعة والدراسات الإسلامية',
    'مجلة القضاء والتشريع',
    'مجلة الحقوق والعلوم الإنسانية',
]

hoqooq_docs = {}
for query in HOQOOQ_QUERIES:
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
        for doc in docs:
            iid = doc.get('identifier', '')
            if iid:
                hoqooq_docs[iid] = doc
        print(f'{query}: {len(docs)} | الإجمالي: {len(hoqooq_docs)}')
    except Exception as e:
        print(f'خطأ: {e}')
    time.sleep(0.4)

hoqooq_clean = []
for iid, doc in hoqooq_docs.items():
    title = doc.get('title', '').strip()
    if not title or len(title) < 4:
        continue
    if is_dirty(title):
        continue
    arabic_chars = sum(1 for c in title if '\u0600' <= c <= '\u06FF')
    if arabic_chars < len(title) * 0.2:
        continue

    creator = doc.get('creator', '')
    if isinstance(creator, list):
        creator = creator[0] if creator else ''
    date = doc.get('date', '')
    if isinstance(date, list):
        date = date[0] if date else ''

    category = classify_hoqooq(title)
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
    hoqooq_clean.append(item)

print(f'\nمجلة الحقوق بعد التصفية: {len(hoqooq_clean)}')

# ===== الخطوة 3: الدمج مع items.json =====
print("\n=== الدمج ===")
with open('/home/ubuntu/makanez-qadaa/items.json', 'r', encoding='utf-8') as f:
    current = json.load(f)

existing_ids = {i['id'] for i in current}

new_items = []
for item in morafaat_clean + hoqooq_clean:
    if item['id'] not in existing_ids:
        new_items.append(item)
        existing_ids.add(item['id'])

merged = current + new_items
print(f'جديد: {len(new_items)} | الإجمالي: {len(merged)}')

with open('/home/ubuntu/makanez-qadaa/items.json', 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)
with open('/home/ubuntu/makanez-qadaa/client/public/items.json', 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

# إحصاءات
from collections import Counter
cats = Counter()
for item in merged:
    cat = item.get('category', '')
    if any(w in cat for w in ['جناي','حدود','قضاء','محكم','مرافع','إثبات','شهاد','أحوال','مجلات','إجراء','مبادئ']):
        cats['قضاء'] += 1
    elif any(w in cat for w in ['نظام','تشريع','إداري','تجاري','عمل']):
        cats['أنظمة'] += 1
    elif any(w in cat for w in ['محاماة','تحكيم']):
        cats['محاماة'] += 1
    else:
        cats['قضاء'] += 1

stats = {
    'total_items': len(merged),
    'with_download_links': len(merged),
    'qadaa_count': cats['قضاء'],
    'nizam_count': cats['أنظمة'],
    'mohama_count': cats['محاماة'],
}
with open('/home/ubuntu/makanez-qadaa/client/public/stats.json', 'w', encoding='utf-8') as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

print('stats:', stats)
print('\nعينة من الجديد:')
for item in new_items[:10]:
    print(f'  [{item["category"]}] {item["title"][:65]}')
