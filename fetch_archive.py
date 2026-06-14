"""
استخراج الكتب القانونية والقضائية العربية من أرشيف الإنترنت
"""
import json
import time
import urllib.request
import urllib.parse
import re

# كلمات مفتاحية للبحث — مرتبة حسب الأولوية
SEARCH_QUERIES = [
    "القضاء الشرعي",
    "القضاء الإداري",
    "قانون العقوبات",
    "قانون الإجراءات الجزائية",
    "قانون المرافعات",
    "قانون الأحوال الشخصية",
    "التحكيم التجاري",
    "المحاماة",
    "الجنايات والحدود",
    "الإثبات في الفقه",
    "نظام القضاء",
    "الأنظمة القضائية",
    "الجريمة والعقوبة",
    "القانون الجنائي",
    "الفقه القضائي",
    "أحكام القضاء",
    "الدعوى القضائية",
    "المحكمة الشرعية",
    "قانون الأسرة",
    "الحقوق القانونية",
]

# كلمات سلبية للاستبعاد
NEGATIVE_WORDS = [
    "الفلسطينية", "الصهيونية", "الإسرائيلية", "السياسة الدولية",
    "الكيمياء", "الفيزياء", "الرياضيات", "الطب", "الهندسة",
    "الأدب", "الشعر", "الرواية", "المسرح", "القصة",
    "التاريخ الإسلامي", "السيرة النبوية", "التفسير", "الحديث",
    "قضية فلسطين", "قضية الجزائر", "قضية مصر",
    "القضاء والقدر", "قضاء الله", "قضاء الحاجة",
    "الاقتصاد", "المحاسبة", "الإدارة العامة",
    "الجغرافيا", "علم النفس", "علم الاجتماع",
]

def normalize(text):
    """تطبيع النص العربي"""
    text = re.sub(r'[أإآا]', 'ا', text)
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = text.replace('ة', 'ه').replace('ى', 'ي')
    return text.lower().strip()

def has_negative(title):
    """فحص الكلمات السلبية"""
    norm = normalize(title)
    for neg in NEGATIVE_WORDS:
        if normalize(neg) in norm:
            return True
    return False

def fetch_archive_items(query, rows=200):
    """استخراج عناصر من أرشيف الإنترنت"""
    items = []
    start = 0
    
    while True:
        params = urllib.parse.urlencode({
            'q': f'{query} AND mediatype:texts AND language:Arabic',
            'output': 'json',
            'rows': rows,
            'start': start,
            'fl': 'identifier,title,creator,subject,date,description',
        })
        url = f'https://archive.org/advancedsearch.php?{params}'
        
        try:
            req = urllib.request.urlopen(url, timeout=15)
            data = json.loads(req.read())
            docs = data['response']['docs']
            total = data['response']['numFound']
            
            if not docs:
                break
                
            items.extend(docs)
            start += rows
            
            if start >= total or start >= 500:  # حد أقصى 500 لكل بحث
                break
                
            time.sleep(0.5)  # احترام حدود الـ API
            
        except Exception as e:
            print(f"  خطأ: {e}")
            break
    
    return items

def classify_category(title, subject=""):
    """تصنيف المادة حسب محتواها"""
    text = normalize(title + " " + str(subject))
    
    if any(w in text for w in ['جناي', 'حدود', 'عقوبه', 'جريمه', 'قانون جنائي', 'قانون عقوبات']):
        return "الجنايات والحدود"
    elif any(w in text for w in ['قضاء اداري', 'مجلس دوله', 'قضاء اداري']):
        return "القضاء الإداري"
    elif any(w in text for w in ['احوال شخصيه', 'اسره', 'زواج', 'طلاق', 'نفقه', 'ميراث', 'وصيه']):
        return "الأحوال الشخصية"
    elif any(w in text for w in ['تحكيم', 'وساطه', 'تسويه']):
        return "التحكيم والوساطة"
    elif any(w in text for w in ['محامي', 'محاماه', 'نقابه محامين']):
        return "المحاماة والتحكيم"
    elif any(w in text for w in ['اثبات', 'شهاده', 'بينه', 'يمين']):
        return "الإثبات والشهادة"
    elif any(w in text for w in ['مرافعات', 'اجراءات', 'دعوى', 'محكمه']):
        return "المحاكم والمرافعات"
    elif any(w in text for w in ['نظام', 'قانون', 'تشريع', 'لائحه']):
        return "الأنظمة والتشريعات"
    else:
        return "القضاء الشرعي"

def classify_section(category):
    """تحديد القسم الرئيسي"""
    if category in ["الأنظمة والتشريعات", "القضاء الإداري"]:
        return "أنظمة"
    elif category in ["المحاماة والتحكيم", "التحكيم والوساطة"]:
        return "محاماة"
    else:
        return "قضاء"

# تشغيل الاستخراج
print("بدء استخراج الكتب من أرشيف الإنترنت...")
all_docs = {}

for query in SEARCH_QUERIES:
    print(f"  بحث: {query}")
    docs = fetch_archive_items(query, rows=100)
    for doc in docs:
        identifier = doc.get('identifier', '')
        if identifier and identifier not in all_docs:
            all_docs[identifier] = doc
    print(f"    → {len(docs)} نتيجة | الإجمالي: {len(all_docs)}")
    time.sleep(0.3)

print(f"\nإجمالي الكتب المستخرجة (قبل التصفية): {len(all_docs)}")

# تصفية وبناء items
new_items = []
skipped = 0

for identifier, doc in all_docs.items():
    title = doc.get('title', '').strip()
    if not title or len(title) < 5:
        skipped += 1
        continue
    
    # استبعاد الكلمات السلبية
    if has_negative(title):
        skipped += 1
        continue
    
    # استبعاد العناوين الإنجليزية
    arabic_chars = sum(1 for c in title if '\u0600' <= c <= '\u06FF')
    if arabic_chars < len(title) * 0.3:
        skipped += 1
        continue
    
    creator = doc.get('creator', '')
    if isinstance(creator, list):
        creator = creator[0] if creator else ''
    
    subject = doc.get('subject', '')
    if isinstance(subject, list):
        subject = ' '.join(subject)
    
    date = doc.get('date', '')
    if isinstance(date, list):
        date = date[0] if date else ''
    
    category = classify_category(title, subject)
    
    item = {
        "id": f"archive_{identifier}",
        "title": title,
        "author": str(creator),
        "investigator": "",
        "publisher": "أرشيف الإنترنت",
        "year": str(date)[:4] if date else "",
        "link_telegram": "",
        "link_drive": "",
        "link_direct": f"https://archive.org/download/{identifier}/{identifier}.pdf",
        "source": "أرشيف الإنترنت",
        "category": category,
        "material_type": "كتاب",
        "file_type": "PDF",
        "file_size": "",
        "pages_count": "",
        "is_featured": False,
        "download_links_count": 1,
    }
    new_items.append(item)

print(f"بعد التصفية: {len(new_items)} مادة (تم استبعاد {skipped})")

# حفظ النتائج
with open('/home/ubuntu/makanez-qadaa/archive_items.json', 'w', encoding='utf-8') as f:
    json.dump(new_items, f, ensure_ascii=False, indent=2)

print(f"\nتم حفظ {len(new_items)} مادة في archive_items.json")

# عرض عينة
print("\nعينة من المواد:")
for item in new_items[:10]:
    print(f"  [{item['category']}] {item['title'][:60]}")
    print(f"    → {item['link_direct']}")
