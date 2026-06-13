"""
استخراج مواد قناة النخبة للاستشارات القانونية
تأخذ فقط الملفات (PDF/Word) ذات الصلة بالقضاء والأنظمة والمحاماة
"""
import json, re, uuid
from pathlib import Path

# كلمات إيجابية للتصفية
POSITIVE_KEYWORDS = [
    'قضاء', 'قضائي', 'قضائية', 'محكمة', 'محاكم', 'قاضي', 'القضاة',
    'نظام', 'أنظمة', 'لائحة', 'لوائح', 'تنظيم',
    'محاماة', 'محامي', 'محامين', 'وكالة', 'دفاع',
    'مذكرة', 'مذكرات', 'لائحة اعتراض', 'طعن', 'استئناف', 'تمييز',
    'عقد', 'عقود', 'صياغة', 'إجراءات', 'جزائي', 'جزائية',
    'إثبات', 'شهادة', 'شهود', 'بينة', 'دعوى', 'دعاوى',
    'حكم', 'أحكام', 'تنفيذ', 'حقوق', 'التزام',
    'قانون', 'قانوني', 'قانونية', 'تشريع', 'تشريعات',
    'وزارة العدل', 'ديوان المظالم', 'هيئة التحقيق', 'النيابة',
    'اعتراض', 'استئناف', 'تمييز', 'نقض',
    'عقوبة', 'عقوبات', 'جريمة', 'جرائم', 'حد', 'حدود',
    'أحوال شخصية', 'زواج', 'طلاق', 'نفقة', 'حضانة', 'ميراث',
    'تجاري', 'تجارية', 'شركة', 'شركات', 'إفلاس',
    'عمالي', 'عمل', 'عمال', 'موظف',
    'ملكية', 'عقار', 'عقارات', 'إيجار',
    'إداري', 'إدارية', 'مظالم',
    'جنائي', 'جنائية', 'جناية', 'جنايات',
    'حقوق الإنسان', 'حقوق المرأة',
]

# كلمات سلبية للاستبعاد
NEGATIVE_KEYWORDS = [
    'قرآن', 'تجويد', 'تفسير', 'حديث', 'سنة', 'فقه العبادات',
    'صلاة', 'زكاة', 'صوم', 'حج', 'عمرة', 'طهارة',
    'عقيدة', 'توحيد', 'إيمان', 'غيبيات',
    'تاريخ', 'سيرة', 'مغازي', 'غزوات',
    'لغة', 'نحو', 'صرف', 'بلاغة', 'أدب',
    'طب', 'رياضيات', 'علوم',
    'file.pdf',  # اسم مجهول
]

def normalize(text):
    """تطبيع النص العربي"""
    text = re.sub(r'[أإآا]', 'ا', text)
    text = re.sub(r'[ةه]', 'ه', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'[_\-]', ' ', text)
    return text.strip()

def is_relevant(title):
    """التحقق من صلة المادة بالموضوع"""
    norm = normalize(title.lower())
    
    # استبعاد الكلمات السلبية
    for neg in NEGATIVE_KEYWORDS:
        if normalize(neg) in norm:
            return False
    
    # قبول الكلمات الإيجابية
    for pos in POSITIVE_KEYWORDS:
        if normalize(pos) in norm:
            return True
    
    return False

def extract_telegram_link(msg):
    """استخراج رابط تيليجرام للرسالة"""
    msg_id = msg.get('id', '')
    return f"https://t.me/alnukhba_legal/{msg_id}" if msg_id else ""

# تحميل الملف
print("جاري تحميل الملف...")
with open('/home/ubuntu/upload/result.json', encoding='utf-8') as f:
    data = json.load(f)

msgs = data.get('messages', [])
channel_name = data.get('name', 'النخبة للاستشارات القانونية')
print(f"القناة: {channel_name}")
print(f"إجمالي الرسائل: {len(msgs)}")

# استخراج المواد
new_items = []
seen_titles = set()

for msg in msgs:
    if msg.get('type') != 'message':
        continue
    
    # الحصول على اسم الملف
    file_name = msg.get('file_name', '') or ''
    
    # تجاهل الرسائل بدون ملفات أو ذات أسماء مجهولة
    if not file_name or file_name in ['file.pdf', 'file.docx']:
        continue
    
    # تنظيف العنوان
    title = re.sub(r'\.(pdf|docx?|xlsx?|zip)$', '', file_name, flags=re.IGNORECASE)
    title = re.sub(r'[_\-]+', ' ', title).strip()
    title = re.sub(r'\s+', ' ', title)
    
    # تجاهل العناوين القصيرة جداً أو المشفرة
    if len(title) < 5 or re.match(r'^[a-zA-Z0-9_\-]+$', title):
        continue
    
    # تجاهل المكررات
    norm_title = normalize(title)
    if norm_title in seen_titles:
        continue
    
    # التحقق من الصلة
    if not is_relevant(title):
        continue
    
    seen_titles.add(norm_title)
    
    # تحديد نوع الملف
    ext = file_name.rsplit('.', 1)[-1].upper() if '.' in file_name else 'PDF'
    if ext not in ['PDF', 'DOC', 'DOCX', 'XLSX', 'ZIP', 'MP3', 'MP4']:
        ext = 'PDF'
    
    # رابط تيليجرام
    link_tg = extract_telegram_link(msg)
    
    # تحديد القسم
    norm = normalize(title.lower())
    if any(k in norm for k in ['محاماة', 'محامي', 'لائحة', 'مذكرة', 'دفاع', 'صياغة', 'لوائح', 'طعن', 'استئناف']):
        category = 'المحاماة والمرافعات'
    elif any(k in norm for k in ['عقد', 'عقود', 'شركة', 'تجاري', 'إفلاس']):
        category = 'العقود والمعاملات التجارية'
    elif any(k in norm for k in ['جزائي', 'جنائي', 'جريمة', 'عقوبة', 'حد', 'جناية']):
        category = 'الجنايات والحدود'
    elif any(k in norm for k in ['نظام', 'لائحة', 'تشريع', 'قانون', 'وزارة العدل']):
        category = 'الأنظمة والتشريعات'
    elif any(k in norm for k in ['أحوال شخصية', 'زواج', 'طلاق', 'نفقة', 'حضانة']):
        category = 'الأحوال الشخصية'
    elif any(k in norm for k in ['إثبات', 'شهادة', 'بينة', 'دعوى']):
        category = 'الإثبات والشهادة'
    elif any(k in norm for k in ['إداري', 'مظالم', 'ديوان']):
        category = 'القضاء الإداري'
    else:
        category = 'القضاء الشرعي'
    
    item = {
        "id": f"nokhba_{msg.get('id', uuid.uuid4().hex[:8])}",
        "title": title,
        "author": "",
        "investigator": "",
        "link_telegram": link_tg,
        "link_drive": "",
        "link_direct": "",
        "source": "قناة النخبة القانونية",
        "category": category,
        "material_type": "بحث",
        "file_type": ext,
        "file_size": "",
        "pages_count": "",
        "is_featured": False,
        "download_links_count": 1 if link_tg else 0
    }
    new_items.append(item)

print(f"\nالمواد المستخرجة: {len(new_items)}")

# عرض عينة
print("\nعينة من المواد:")
for item in new_items[:20]:
    print(f"  [{item['category']}] {item['title']}")

# دمج مع items.json الحالي
with open('/home/ubuntu/makanez-qadaa/items.json', encoding='utf-8') as f:
    existing = json.load(f)

existing_ids = {i['id'] for i in existing}
added = [i for i in new_items if i['id'] not in existing_ids]
merged = existing + added

with open('/home/ubuntu/makanez-qadaa/items.json', 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False)

import shutil
shutil.copy('/home/ubuntu/makanez-qadaa/items.json', '/home/ubuntu/makanez-qadaa/client/public/items.json')

print(f"\nتم إضافة: {len(added)} مادة جديدة")
print(f"الإجمالي الجديد: {len(merged)} مادة")

# توزيع الأقسام
cats = {}
for i in added:
    cats[i['category']] = cats.get(i['category'], 0) + 1
print("\nتوزيع الأقسام:")
for c, n in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {n:4d}  {c}")
