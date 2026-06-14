#!/usr/bin/env python3
"""
تصفية صارمة جداً لقناة الرسائل العلمية
نريد فقط ما يرتبط مباشرة بالقضاء والأنظمة والمحاماة
"""

import json
import re
from collections import Counter

CHANNEL_ID = 1453973283

# ===== كلمات إيجابية صارمة جداً =====
# يجب أن يحتوي اسم الملف على واحدة منها على الأقل
STRICT_POSITIVE = [
    # القضاء المباشر
    'قضاء', 'قضائي', 'قضائية', 'القاضي', 'القضاة', 'أدب القاضي',
    'آداب القضاء', 'ولاية القضاء', 'شروط القاضي', 'القضاء الشرعي',
    'القضاء الإداري', 'القضاء الجنائي', 'القضاء التجاري', 'القضاء الدولي',
    'المحكمة', 'المحاكم', 'محكمة التمييز', 'محكمة الاستئناف',
    'التقاضي', 'الدعوى القضائية', 'الدعاوى القضائية',
    'الخصومة القضائية', 'الحكم القضائي', 'الأحكام القضائية',
    'التنفيذ القضائي', 'الاختصاص القضائي',
    'الاستئناف', 'التمييز القضائي', 'النقض', 'الطعن القضائي',
    # الإجراءات
    'المرافعات', 'إجراءات التقاضي', 'الإجراءات القضائية',
    'إثبات قضائي', 'الإثبات في القضاء', 'الشهادة في القضاء',
    'اليمين القضائية', 'القرائن القضائية',
    # الجنايات والعقوبات
    'الجنايات', 'الجناية', 'الجنح', 'الجرائم والعقوبات',
    'الحدود الشرعية', 'القصاص', 'التعزير', 'الجنائي',
    'العقوبات الشرعية', 'الجريمة والعقوبة',
    'جرائم القتل', 'جرائم السرقة', 'جرائم الاغتصاب',
    'جرائم الإرهاب', 'جرائم الفساد', 'جرائم المعلوماتية',
    'جرائم الاتجار', 'الجرائم الإلكترونية', 'الجرائم المالية',
    'الجرائم الأسرية', 'جرائم الأحداث', 'جرائم المخدرات',
    # الأنظمة والقوانين المباشرة
    'نظام المرافعات', 'نظام الإجراءات الجزائية',
    'نظام الإجراءات المدنية', 'نظام التنفيذ',
    'نظام الإثبات', 'نظام الأحوال الشخصية',
    'نظام العمل والعمال', 'نظام الشركات',
    'نظام الأوراق التجارية', 'نظام التجارة',
    'نظام مكافحة الفساد', 'نظام الإفلاس',
    'نظام التحكيم', 'نظام الوساطة',
    'نظام حماية الطفل', 'نظام مكافحة الاتجار',
    'القانون الجنائي', 'القانون المدني', 'القانون التجاري',
    'القانون الإداري', 'القانون الدولي الخاص',
    'القانون الدولي العام', 'القانون الإجرائي',
    'قانون العقوبات', 'قانون المرافعات',
    'التشريع الجنائي', 'التشريع القضائي',
    'تقنين الأحوال الشخصية', 'تقنين الفقه الإسلامي',
    # المحاماة
    'المحامي', 'المحاماة', 'المحامون', 'مهنة المحاماة',
    'الوكيل القضائي', 'الوكالة القضائية', 'الترافع',
    'نقابة المحامين', 'أتعاب المحاماة', 'سر المهنة للمحامي',
    'مسؤولية المحامي',
    # التحكيم
    'التحكيم التجاري', 'التحكيم الدولي', 'التحكيم الإلكتروني',
    'هيئة التحكيم', 'المحكم', 'حكم التحكيم',
    'الوساطة القضائية', 'الصلح القضائي',
    # الأحوال الشخصية القضائية
    'الطلاق القضائي', 'الخلع القضائي', 'فسخ الزواج',
    'النفقة القضائية', 'الحضانة القضائية',
    'إثبات النسب', 'إثبات الزواج', 'إثبات الطلاق',
    'الميراث القضائي', 'التركات القضائية',
    # السجون والإصلاح
    'السجون', 'السجين', 'المسجون', 'الإصلاح الجنائي',
    'رعاية السجناء', 'إعادة التأهيل الجنائي',
]

# ===== كلمات استبعاد موسعة =====
STRICT_NEGATIVE = [
    # غير قانوني
    'قضاء وقدر', 'القضاء والقدر', 'قدر الله', 'الدعاء ذريعة',
    'شفاء العليل في القضاء', 'قضية فلسطين', 'القضية الفلسطينية',
    'قضية الجلاء', 'القضية الكشميرية',
    # أدب وفنون
    'مسرحية', 'رواية', 'قصة', 'ديوان', 'شعر', 'أدب',
    # علوم أخرى
    'الكيمياء', 'الفيزياء', 'الأحياء', 'الرياضيات', 'الجيولوجيا',
    'الجغرافيا', 'الفلك', 'الطب النووي',
    # إدارة عامة غير قضائية
    'الأداء الوظيفي', 'الحوكمة المؤسسية', 'إدارة الموارد البشرية',
    'التسويق', 'المحاسبة', 'الاقتصاد الكلي',
    # تربية وتعليم
    'التربية والتعليم', 'المناهج الدراسية', 'التحصيل الدراسي',
    # طب وصحة
    'الأمراض', 'العلاج', 'الصحة النفسية', 'الطب الشرعي غير القضائي',
    # سياسة غير قانونية
    'السياسة الخارجية', 'العلاقات الدولية السياسية',
    # أنف وأعضاء جسم (فقه طبي)
    'المتعلقة بالأنف', 'أحكام الأنف', 'أحكام العين',
    # حوكمة غير قضائية
    'خصائص الحكمانية',
]

def normalize(text):
    if not text:
        return ''
    text = text.lower()
    text = re.sub(r'[أإآا]', 'ا', text)
    text = re.sub(r'[يى]', 'ي', text)
    text = re.sub(r'ة', 'ه', text)
    return text

def matches_strict_positive(name):
    norm = normalize(name)
    for kw in STRICT_POSITIVE:
        if normalize(kw) in norm:
            return True
    return False

def matches_strict_negative(name):
    norm = normalize(name)
    for kw in STRICT_NEGATIVE:
        if normalize(kw) in norm:
            return True
    return False

def clean_filename(fname):
    name = re.sub(r'\.(pdf|PDF)$', '', fname, flags=re.IGNORECASE)
    name = name.replace('_', ' ')
    name = re.sub(r'^\d+[\.\-\s]+', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def extract_author(title):
    parts = re.split(r'[-–]', title)
    if len(parts) >= 2:
        author = parts[-1].strip()
        if 2 < len(author) < 50 and not any(c.isdigit() for c in author[:3]):
            return author
    return ''

def categorize(name):
    norm = normalize(name)
    
    if any(normalize(k) in norm for k in ['محامي', 'محاماة', 'المحامون', 'المحامين', 'الترافع', 'نقابة المحامين', 'مسؤولية المحامي', 'سر المهنة']):
        return 'المحاماة'
    
    if any(normalize(k) in norm for k in ['تحكيم', 'المحكم', 'وساطة قضائية', 'صلح قضائي']):
        return 'التحكيم والوساطة'
    
    if any(normalize(k) in norm for k in ['جناية', 'جنايات', 'جنائي', 'عقوبات', 'حدود شرعية', 'قصاص', 'تعزير', 'جرائم', 'جريمة والعقوبة', 'سجون', 'سجين']):
        return 'الجنايات والعقوبات'
    
    if any(normalize(k) in norm for k in ['مرافعات', 'إجراءات', 'تقاضي', 'دعوى', 'خصومة', 'إثبات', 'استئناف', 'تمييز', 'نقض', 'طعن']):
        return 'الإجراءات القضائية'
    
    if any(normalize(k) in norm for k in ['أحوال شخصية', 'طلاق قضائي', 'خلع', 'نفقة', 'حضانة', 'نسب', 'ميراث قضائي', 'تركات']):
        return 'الأحوال الشخصية'
    
    if any(normalize(k) in norm for k in ['نظام', 'قانون', 'لائحة', 'تشريع', 'تقنين']):
        return 'الأنظمة والتشريعات'
    
    return 'القضاء الشرعي'

# ===== تحميل =====
print("تحميل البيانات...")
with open('/home/ubuntu/upload/result.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

msgs = data['messages']
pdf_msgs = [m for m in msgs if m.get('mime_type') == 'application/pdf' and m.get('file_name')]
print(f"PDF: {len(pdf_msgs)}")

# ===== تصفية صارمة =====
matched = []
excluded_neg = 0
excluded_no_match = 0

for m in pdf_msgs:
    fname = m.get('file_name', '')
    if not fname:
        continue
    if matches_strict_negative(fname):
        excluded_neg += 1
        continue
    if matches_strict_positive(fname):
        matched.append(m)
    else:
        excluded_no_match += 1

print(f"مستبعد (كلمات سلبية): {excluded_neg}")
print(f"مستبعد (لا تطابق): {excluded_no_match}")
print(f"المطابق: {len(matched)}")

# ===== بناء العناصر =====
items = []
for m in matched:
    fname = m.get('file_name', '')
    msg_id = m.get('id')
    title = clean_filename(fname)
    author = extract_author(title)
    # إزالة اسم المؤلف من العنوان إذا وُجد
    if author and title.endswith(f'- {author}'):
        title = title[:-len(f'- {author}')].strip()
    
    category = categorize(fname)
    tg_link = f"https://t.me/c/{CHANNEL_ID}/{msg_id}"
    
    items.append({
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
    })

print(f"\nعناصر جاهزة: {len(items)}")

# ===== حفظ =====
with open('/home/ubuntu/makanez-qadaa/risail_items_strict.json', 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

# ===== إحصاءات =====
cats = Counter(i['category'] for i in items)
print("\nتوزيع الأقسام:")
for cat, count in cats.most_common():
    print(f"  {cat}: {count}")

print("\nعينة من كل قسم:")
from collections import defaultdict
by_cat = defaultdict(list)
for i in items:
    by_cat[i['category']].append(i['title'])
for cat, titles in by_cat.items():
    print(f"\n[{cat}]")
    for t in titles[:4]:
        print(f"  - {t[:80]}")
