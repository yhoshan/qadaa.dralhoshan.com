#!/usr/bin/env python3
"""
تصفية قناة الرسائل العلمية والبحوث المحكمة
واستخراج المواد المتعلقة بالقضاء والأنظمة والمحاماة
وبناء روابط تيليجرام من message_id
"""

import json
import re
import uuid
from pathlib import Path
from title_scope_gate import intake_decision

# ===== إعدادات القناة =====
CHANNEL_ID = 1453973283  # ID القناة من result.json

# ===== كلمات البحث الإيجابية =====
POSITIVE_KEYWORDS = [
    # القضاء
    'قضاء', 'قضائي', 'قضائية', 'القاضي', 'القضاة', 'المحكمة', 'المحاكم',
    'الحكم القضائي', 'الأحكام القضائية', 'التقاضي', 'الدعوى', 'الدعاوى',
    'الخصومة', 'المرافعة', 'المرافعات', 'الإثبات', 'الشهادة', 'اليمين',
    'القضاء الشرعي', 'القضاء الإداري', 'القضاء الجنائي', 'القضاء التجاري',
    'الاستئناف', 'التمييز', 'النقض', 'الطعن', 'الحكم', 'الأحكام',
    'الإجراءات القضائية', 'التنفيذ القضائي', 'الاختصاص القضائي',
    'القضاء الدولي', 'التحكيم', 'الوساطة', 'الصلح القضائي',
    'أدب القاضي', 'آداب القضاء', 'ولاية القضاء', 'شروط القاضي',
    'الجرائم', 'الجريمة', 'العقوبات', 'العقوبة', 'الحدود', 'القصاص',
    'التعزير', 'الجنايات', 'الجناية', 'الجنح', 'المخالفات',
    'السجن', 'الغرامة', 'الإعدام', 'الجلد',
    # الأنظمة
    'نظام', 'الأنظمة', 'اللوائح', 'اللائحة', 'التشريع', 'التشريعات',
    'القانون', 'القوانين', 'الفقه القانوني', 'الفقه الإجرائي',
    'نظام المرافعات', 'نظام الإجراءات', 'نظام العمل', 'نظام الأحوال',
    'نظام التنفيذ', 'نظام الإثبات', 'نظام الأوراق التجارية',
    'نظام الشركات', 'نظام التجارة', 'النظام الجزائي',
    'الأنظمة السعودية', 'الأنظمة الإدارية', 'الأنظمة المالية',
    'التقنين', 'تقنين الفقه', 'التقنين الفقهي',
    # المحاماة
    'محامي', 'محاماة', 'المحامون', 'المحامين', 'المحامي',
    'الوكالة القضائية', 'الوكيل القضائي', 'الترافع',
    'نقابة المحامين', 'مهنة المحاماة', 'أتعاب المحاماة',
    # الأحوال الشخصية والمدنية
    'الأحوال الشخصية', 'الزواج والطلاق', 'النفقة', 'الحضانة',
    'الميراث والتركات', 'الوصية', 'الوقف',
    'عقد الزواج', 'فسخ الزواج', 'الخلع', 'الطلاق القضائي',
    # الإدارة والمالية
    'الإدارة القضائية', 'المال العام', 'الضرائب', 'الجمارك',
    'الإدارة العامة', 'القانون الإداري', 'الطعن الإداري',
    # الدولي
    'القانون الدولي', 'المعاهدات', 'الاتفاقيات الدولية',
    'حقوق الإنسان', 'القانون الإنساني',
]

# ===== كلمات الاستبعاد =====
NEGATIVE_KEYWORDS = [
    'قضية فلسطين', 'القضية الفلسطينية', 'قضية الجلاء',
    'قضاء وقدر', 'القضاء والقدر', 'قدر الله',
    'الدعاء ذريعة', 'شفاء العليل',
    'مسرحية', 'رواية', 'قصة', 'ديوان شعر',
    'الكيمياء', 'الفيزياء', 'الأحياء', 'الرياضيات',
    'التربية والتعليم', 'المناهج الدراسية',
    'الجغرافيا', 'التاريخ الطبيعي',
    'النووي الكيميائي', 'النووي البيولوجي',
]

def normalize_arabic(text):
    """تطبيع النص العربي لتسهيل البحث"""
    if not text:
        return ''
    text = text.lower()
    # توحيد الهمزات
    text = re.sub(r'[أإآا]', 'ا', text)
    # توحيد الياء
    text = re.sub(r'[يى]', 'ي', text)
    # توحيد الهاء والتاء المربوطة
    text = re.sub(r'ة', 'ه', text)
    return text

def matches_positive(name):
    norm = normalize_arabic(name)
    for kw in POSITIVE_KEYWORDS:
        if normalize_arabic(kw) in norm:
            return True
    return False

def matches_negative(name):
    norm = normalize_arabic(name)
    for kw in NEGATIVE_KEYWORDS:
        if normalize_arabic(kw) in norm:
            return True
    return False

def clean_filename(fname):
    """تنظيف اسم الملف ليصبح عنواناً"""
    # إزالة الامتداد
    name = re.sub(r'\.(pdf|PDF|docx?|rar|zip)$', '', fname, flags=re.IGNORECASE)
    # استبدال الشرطة السفلية بمسافة
    name = name.replace('_', ' ')
    # إزالة الأرقام في البداية
    name = re.sub(r'^\d+[\.\-\s]+', '', name)
    # تنظيف المسافات المتعددة
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def extract_author(name):
    """محاولة استخراج اسم المؤلف من اسم الملف"""
    # البحث عن نمط "العنوان - المؤلف" أو "العنوان_المؤلف"
    parts = re.split(r'[-–]', name)
    if len(parts) >= 2:
        # الجزء الأخير غالباً هو المؤلف
        author = parts[-1].strip()
        if 2 < len(author) < 50:
            return author
    return ''

def categorize(name):
    """تصنيف المادة"""
    norm = normalize_arabic(name)
    
    if any(normalize_arabic(k) in norm for k in ['محامي', 'محاماة', 'المحامون', 'المحامين', 'الترافع', 'نقابة المحامين']):
        return 'المحاماة'
    
    if any(normalize_arabic(k) in norm for k in ['نظام', 'قانون', 'لائحة', 'تشريع', 'تقنين', 'القانون الإداري', 'القانون الدولي']):
        return 'الأنظمة والتشريعات'
    
    if any(normalize_arabic(k) in norm for k in ['جريمة', 'جرائم', 'عقوبة', 'عقوبات', 'حدود', 'قصاص', 'تعزير', 'جنايات', 'جنائي']):
        return 'الجنايات والحدود'
    
    if any(normalize_arabic(k) in norm for k in ['مرافعة', 'مرافعات', 'إجراءات', 'تقاضي', 'دعوى', 'دعاوى', 'خصومة', 'إثبات']):
        return 'الإجراءات القضائية'
    
    if any(normalize_arabic(k) in norm for k in ['أحوال شخصية', 'زواج', 'طلاق', 'نفقة', 'حضانة', 'ميراث', 'وصية', 'وقف']):
        return 'الأحوال الشخصية'
    
    if any(normalize_arabic(k) in norm for k in ['تحكيم', 'وساطة', 'صلح']):
        return 'التحكيم والوساطة'
    
    return 'القضاء الشرعي'

# ===== تحميل البيانات =====
print("تحميل بيانات القناة...")
with open('/home/ubuntu/upload/result.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

msgs = data['messages']
print(f"إجمالي الرسائل: {len(msgs)}")

# ===== تصفية PDF =====
pdf_msgs = [m for m in msgs if m.get('mime_type') == 'application/pdf' and m.get('file_name')]
print(f"ملفات PDF: {len(pdf_msgs)}")

# ===== تطبيق التصفية =====
matched = []
review_needed = []
for m in pdf_msgs:
    fname = m.get('file_name', '')
    if not fname:
        continue
    
    if matches_negative(fname):
        continue
    
    if matches_positive(fname):
        if intake_decision(clean_filename(fname)) != 'CANDIDATE':
            review_needed.append({"file_name": fname, "message_id": m.get('id', '')})
            continue
        matched.append(m)

print(f"المطابق للمكنز: {len(matched)}")
print(f"تحتاج مراجعة دلالية قبل الدمج: {len(review_needed)}")

with open('/home/ubuntu/makanez-qadaa/risail_review_needed.json', 'w', encoding='utf-8') as f:
    json.dump(review_needed, f, ensure_ascii=False, indent=2)

# ===== بناء عناصر items.json =====
items = []
for m in matched:
    fname = m.get('file_name', '')
    msg_id = m.get('id')
    
    title = clean_filename(fname)
    author = extract_author(title)
    category = categorize(fname)
    
    # بناء رابط تيليجرام
    tg_link = f"https://t.me/c/{CHANNEL_ID}/{msg_id}"
    
    item = {
        "id": f"risail_{msg_id}",
        "title": title,
        "author": author,
        "investigator": "",
        "link_telegram": tg_link,
        "link_drive": "",
        "link_direct": "",
        "source": "قناة الرسائل العلمية",
        "category": category,
        "material_type": "رسالة علمية",
        "file_type": "PDF",
        "file_size": "",
        "pages_count": "",
        "is_featured": False,
        "download_links_count": 1
    }
    items.append(item)

print(f"\nعناصر جاهزة للإضافة: {len(items)}")

# ===== عرض عينة =====
print("\nعينة من المواد المستخرجة:")
for item in items[:15]:
    print(f"  [{item['category']}] {item['title'][:70]}")

# ===== حفظ الملف المؤقت =====
with open('/home/ubuntu/makanez-qadaa/risail_items.json', 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"\nتم حفظ {len(items)} عنصر في risail_items.json")

# ===== إحصاءات التصنيف =====
from collections import Counter
cats = Counter(i['category'] for i in items)
print("\nتوزيع الأقسام:")
for cat, count in cats.most_common():
    print(f"  {cat}: {count}")
