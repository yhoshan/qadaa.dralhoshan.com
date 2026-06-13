#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
استخراج المواد القضائية من قناة "جامعة الرسائل العلمية"
وإضافتها إلى items.json
"""

import json
import re
from pathlib import Path

UPLOAD_FILE = "/home/ubuntu/upload/result.json"
ITEMS_FILE = "/home/ubuntu/makanez-qadaa/items.json"

# كلمات مفتاحية للقضاء والأنظمة والمحاماة
QADAA_KEYWORDS = [
    # القضاء الشرعي
    "قضاء", "قضائ", "قضاة", "قاضي", "محكم", "محاكم", "محكمة",
    # الجنايات والحدود
    "جنائ", "جناي", "جنايات", "حدود", "قصاص", "دية", "تعزير",
    "عقوبات", "جريمة", "جرائم", "سرقة", "قتل", "قذف", "زنا",
    # المرافعات والإثبات
    "مرافعات", "إثبات", "اثبات", "شهادة", "شهود", "بينة", "يمين",
    "دعوى", "دعاوى", "خصومة",
    # الأنظمة والتشريعات
    "نظام العمل", "نظام الأحوال", "نظام المرافعات", "نظام الإثبات",
    "نظام العقوبات", "نظام التحكيم", "نظام الإفلاس", "نظام الشركات",
    "نظام التجاري", "نظام الجزائي", "نظام الإداري",
    # المحاماة والتحكيم
    "محاماة", "محامي", "تحكيم", "وساطة", "مستشار قانوني",
    # الفرائض والمواريث
    "فرائض", "ميراث", "إرث", "مواريث", "وصية", "تركة",
    # الأحوال الشخصية
    "طلاق", "خلع", "نفقة", "حضانة", "نكاح", "زواج", "مهر",
    # الوقف
    "وقف", "أوقاف", "ناظر وقف",
    # المظالم والحسبة
    "مظالم", "حسبة", "ديوان المظالم",
    # القضاء الإداري
    "قضاء إداري", "إداري",
    # الأحكام القضائية
    "أحكام قضائية", "مبادئ قضائية", "قرارات قضائية", "سوابق قضائية",
    "أحكام_اختطاف", "أحكام_التخدير", "أحكام_التفحيط",
    "إجراءات_التنفيذ", "أحكام_أجر_العامل",
    # الرسائل القضائية
    "أثر_الزوجية_في_الجنايات", "أثر_مصلحة_المحضون",
    "إثبات_النسب", "أثر_الخلاف_في_مسائل_الحكم",
    "أثر_المخالفات_الشرعية_والنظامية",
]

# كلمات مفتاحية للاستبعاد (غير ذات صلة)
EXCLUDE_KEYWORDS = [
    "هندسة", "معمار", "كيمياء", "فيزياء", "رياضيات", "طب", "صيدلة",
    "زراعة", "بيولوجيا", "جيولوجيا", "تصميم", "فراغات", "مباني",
    "خرسانة", "بيتون", "ميكانيك", "كهرباء", "حاسوب", "برمجة",
    "ويب", "شبكات", "اقتصاد", "محاسبة", "إدارة أعمال", "تسويق",
    "نفس", "تربية", "لغة", "أدب", "تاريخ", "جغرافيا",
]

def is_qadaa_related(fname):
    """تحديد ما إذا كان الملف متعلقاً بالقضاء"""
    fname_lower = fname.lower()
    
    # استبعاد الكلمات غير ذات الصلة
    for excl in EXCLUDE_KEYWORDS:
        if excl in fname_lower:
            return False
    
    # البحث عن كلمات مفتاحية
    for kw in QADAA_KEYWORDS:
        if kw.lower() in fname_lower:
            return True
    
    return False

def get_category(fname):
    """تحديد القسم"""
    n = fname.lower()
    if any(k in n for k in ["جنائ", "جناي", "جنايات", "حدود", "قصاص", "دية", "تعزير", "عقوبات", "جريمة", "جرائم", "سرقة", "قتل", "قذف", "اختطاف", "تفحيط", "تخدير"]):
        return "الجنايات والحدود"
    elif any(k in n for k in ["مرافعات", "إجراءات", "دعوى", "خصومة", "تنفيذ"]):
        return "المحاكم والمرافعات"
    elif any(k in n for k in ["إثبات", "اثبات", "شهادة", "شهود", "بينة", "يمين", "نسب", "بصمة"]):
        return "الإثبات والشهادة"
    elif any(k in n for k in ["محاماة", "محامي", "تحكيم", "وساطة", "مستشار"]):
        return "المحاماة والتحكيم"
    elif any(k in n for k in ["فرائض", "ميراث", "إرث", "مواريث", "وصية", "تركة"]):
        return "الفرائض والمواريث"
    elif any(k in n for k in ["طلاق", "خلع", "نفقة", "حضانة", "نكاح", "زواج", "مهر", "أحوال شخصية", "أسرة", "محضون"]):
        return "الأحوال الشخصية"
    elif any(k in n for k in ["وقف", "أوقاف", "ناظر"]):
        return "القضاء الشرعي"
    elif any(k in n for k in ["مظالم", "حسبة", "ديوان"]):
        return "الحسبة والمظالم"
    elif any(k in n for k in ["إداري", "مظالم"]):
        return "القضاء الإداري"
    elif any(k in n for k in ["نظام", "أنظمة", "لائحة", "تشريع", "قانون"]):
        return "الأنظمة والتشريعات"
    elif any(k in n for k in ["أحكام", "مبادئ", "قرارات", "سوابق"]):
        return "المبادئ والقرارات القضائية"
    elif any(k in n for k in ["قضاء", "قضائ", "قضاة", "قاضي", "محكم", "محاكم"]):
        return "القضاء الشرعي"
    else:
        return "أبحاث ودراسات قضائية"

def get_material_type(fname):
    """تحديد نوع المادة"""
    n = fname.lower()
    if any(k in n for k in ["رسالة ماجستير", "ماجستير", "رسالة_ماجستير"]):
        return "رسالة ماجستير"
    elif any(k in n for k in ["رسالة دكتوراه", "دكتوراه", "رسالة_دكتوراه"]):
        return "رسالة دكتوراه"
    elif any(k in n for k in ["بحث", "دراسة"]):
        return "بحث"
    elif any(k in n for k in ["شرح", "تعليق"]):
        return "شرح"
    elif any(k in n for k in ["متن", "نظم"]):
        return "متن"
    else:
        return "بحث"

def clean_title(fname):
    """تنظيف اسم الملف"""
    title = fname
    title = re.sub(r'\.(pdf|PDF|rar|zip|doc|docx)$', '', title)
    title = title.replace('_', ' ')
    title = re.sub(r'^\d+[-\s]*', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    # إزالة بعض البادئات الشائعة
    for prefix in ["Noor_Book_com_", "noor_book_"]:
        if title.lower().startswith(prefix.lower()):
            title = title[len(prefix):]
    return title.strip()

def normalize(text):
    text = re.sub(r'[أإآا]', 'ا', text)
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = re.sub(r'ة', 'ه', text)
    return text.strip().lower()

def format_size(bytes_val):
    if bytes_val > 1024*1024:
        return f"{bytes_val/(1024*1024):.1f} MB"
    elif bytes_val > 1024:
        return f"{bytes_val/1024:.1f} KB"
    return f"{bytes_val} B"

# ==============================
# استخراج بيانات الملفات
# ==============================
print("📖 قراءة ملف الرسائل العلمية (37 MB)...")

with open(UPLOAD_FILE, encoding="utf-8", errors="replace") as f:
    raw = f.read()

# استخراج أسماء الملفات وأحجامها
file_names = re.findall(r'"file_name":\s*"([^"]+\.(?:pdf|PDF|rar|zip|doc|docx))"', raw)
file_sizes_raw = re.findall(r'"file_size":\s*(\d+)', raw)

print(f"📄 إجمالي الملفات: {len(file_names)}")

# تصفية الملفات المتعلقة بالقضاء
qadaa_files = [(fname, i) for i, fname in enumerate(file_names) if is_qadaa_related(fname)]
print(f"⚖️ ملفات قضائية: {len(qadaa_files)}")

# ==============================
# قراءة items.json الحالي
# ==============================
with open(ITEMS_FILE, encoding="utf-8") as f:
    items = json.load(f)

print(f"📊 مواد حالية: {len(items)}")

# تتبع العناوين الموجودة
seen_titles = {normalize(item["title"]) for item in items}
last_id = len(items)

new_items = []
added = 0
skipped_dup = 0

for fname, idx in qadaa_files:
    title = clean_title(fname)
    if len(title) < 8:
        continue
    
    title_norm = normalize(title)
    if title_norm in seen_titles:
        skipped_dup += 1
        continue
    seen_titles.add(title_norm)
    
    last_id += 1
    
    # حجم الملف
    size_bytes = int(file_sizes_raw[idx]) if idx < len(file_sizes_raw) else 0
    file_size = format_size(size_bytes) if size_bytes > 0 else ""
    
    # نوع الملف
    ext = fname.split('.')[-1].lower() if '.' in fname else 'pdf'
    file_type_map = {'pdf': 'PDF', 'rar': 'ZIP', 'zip': 'ZIP', 'doc': 'Word', 'docx': 'Word'}
    file_type = file_type_map.get(ext, 'PDF')
    
    category = get_category(fname)
    material_type = get_material_type(fname)
    
    new_items.append({
        "id": f"rasail_{last_id:05d}",
        "title": title,
        "author": "",
        "investigator": "",
        "publisher": "جامعة الرسائل العلمية",
        "year": "",
        "link_telegram": "https://t.me/Arsail2020",
        "link_drive": "",
        "link_direct": "",
        "source": "جامعة الرسائل العلمية",
        "category": category,
        "material_type": material_type,
        "file_type": file_type,
        "file_size": file_size,
        "pages_count": "",
        "is_featured": any(k in fname for k in ["ماجستير", "دكتوراه"]) and any(k in fname for k in ["قضاء", "جنائ", "مرافعات", "إثبات"]),
        "download_links_count": 1
    })
    added += 1

print(f"✅ مواد جديدة من الرسائل العلمية: {added}")
print(f"⏭️ مكررة تم تخطيها: {skipped_dup}")

# دمج المواد
items.extend(new_items)

# حفظ
with open(ITEMS_FILE, "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"📊 إجمالي المواد بعد الإضافة: {len(items):,}")

# تحديث الإحصاءات
from collections import Counter
cats = Counter(item["category"] for item in items)
sources = Counter(item["source"] for item in items)
file_types = Counter(item["file_type"] for item in items)
material_types = Counter(item["material_type"] for item in items)

stats = {
    "total_items": len(items),
    "categories": dict(cats.most_common()),
    "sources": dict(sources.most_common()),
    "file_types": dict(file_types.most_common()),
    "material_types": dict(material_types.most_common()),
    "featured_count": sum(1 for item in items if item.get("is_featured")),
    "with_download_links": sum(1 for item in items if item.get("download_links_count", 0) > 0),
    "telegram_channels": [
        "مفضلة اللجان شبه القضائية",
        "جامعة الرسائل العلمية — https://t.me/Arsail2020",
        "المستشارون السعوديون — https://t.me/saudiattorneys",
        "المكتبة القانونية — https://t.me/Ymtaz",
        "ألق للدورات القانونية — https://t.me/AlaqPlatform",
    ]
}

with open("/home/ubuntu/makanez-qadaa/stats.json", "w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

print(f"\n📊 الإحصاءات النهائية:")
print(f"  إجمالي المواد: {len(items):,}")
print(f"  المواد المميزة: {stats['featured_count']:,}")
print(f"  لها روابط تحميل: {stats['with_download_links']:,}")
print(f"\n  الأقسام:")
for cat, count in cats.most_common():
    print(f"    {cat}: {count:,}")
print(f"\n  أنواع المواد:")
for mt, count in material_types.most_common():
    print(f"    {mt}: {count:,}")
print(f"\n  المصادر الرئيسية:")
for src, count in sources.most_common(8):
    print(f"    {src}: {count:,}")
