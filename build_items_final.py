#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
بناء ملف items.json المعياري لمكنز القضاء والأنظمة والمحاماة
"""

import pandas as pd
import json
import re
import os
from pathlib import Path

DATA_DIR = Path("/home/ubuntu/makanez-qadaa/data")
OUTPUT_DIR = Path("/home/ubuntu/makanez-qadaa")

def normalize_arabic(text):
    """تطبيع النص العربي للبحث"""
    if not isinstance(text, str):
        return ""
    text = re.sub(r'[أإآا]', 'ا', text)
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'ى', 'ي', text)
    return text.strip().lower()

def clean(text):
    """تنظيف النص"""
    if not isinstance(text, str) or text.strip() in ["nan", "None", ""]:
        return ""
    return text.strip()

def extract_telegram_link(text):
    """استخراج رابط تيليجرام"""
    if not isinstance(text, str):
        return ""
    match = re.search(r'https://t\.me/\S+', text)
    return match.group(0).rstrip('.,;') if match else ""

def extract_file_size(text):
    """استخراج حجم الملف"""
    if not isinstance(text, str):
        return ""
    # البحث عن الأرقام الكبيرة (bytes)
    match = re.search(r'(\d{4,})', text)
    if match:
        size_bytes = int(match.group(1))
        if size_bytes > 1024*1024:
            return f"{size_bytes/(1024*1024):.1f} MB"
        elif size_bytes > 1024:
            return f"{size_bytes/1024:.1f} KB"
    return ""

# الكلمات المفتاحية الأساسية للقضاء والأنظمة والمحاماة
CORE_KEYWORDS = [
    "قضاء", "قاضي", "قضاه", "قضائي", "قضائيه",
    "محكمه", "محاكم", "مرافعات",
    "جنايات", "جنايه", "حدود", "قصاص", "ديات", "ديه", "تعزير",
    "شهاده", "شهود", "اثبات", "بينه", "يمين", "اقرار",
    "دعوى", "دعاوي", "خصومه", "تقاضي",
    "نظام الاحوال الشخصيه", "نظام المرافعات", "نظام الاجراءات",
    "نظام العمل", "نظام الشركات",
    "محاماه", "محامي", "تحكيم",
    "حسبه", "محتسب", "مظالم",
    "فقه جنائي", "فقه قانوني",
    "اداب القضاء", "ولايه القضاء",
    "الحكم بالقرائن", "قرائن قضائيه",
    "فقه القضاء",
]

# الكلمات المفتاحية الموسعة
EXTENDED_KEYWORDS = [
    "نظام", "انظمه", "تشريع", "تشريعات", "لائحه", "لوائح",
    "قانون", "قانوني", "قانونيه",
    "طلاق", "خلع", "فسخ", "نفقه", "حضانه",
    "ميراث", "ارث", "فرائض", "مواريث", "تركه",
    "وقف", "الاوقاف",
    "عقوبه", "عقوبات", "جرائم", "جريمه",
    "الفقه الجنائي", "الفقه الاسلامي والقانون",
    "السياسه الشرعيه",
    "الولايه", "الوصايه", "الوكاله",
    "الصلح", "الوساطه",
]

def is_core_relevant(text):
    """فحص الصلة الأساسية"""
    norm = normalize_arabic(text)
    return any(kw in norm for kw in CORE_KEYWORDS)

def is_extended_relevant(text):
    """فحص الصلة الموسعة"""
    norm = normalize_arabic(text)
    return any(kw in norm for kw in EXTENDED_KEYWORDS)

def determine_category(title, section=""):
    """تحديد القسم"""
    combined = normalize_arabic(title + " " + section)
    
    if any(k in combined for k in ["قضاء", "قاضي", "قضاه", "اداب القضاء", "ولايه القضاء", "فقه القضاء"]):
        return "القضاء الشرعي"
    elif any(k in combined for k in ["نظام", "انظمه", "تشريع", "لائحه", "قانون"]):
        return "الأنظمة والتشريعات"
    elif any(k in combined for k in ["محكمه", "محاكم", "مرافعات", "اجراءات", "تقاضي", "دعوى", "دعاوي"]):
        return "المحاكم والمرافعات"
    elif any(k in combined for k in ["اثبات", "شهاده", "شهود", "بينه", "يمين", "اقرار", "قرائن"]):
        return "الإثبات والشهادة"
    elif any(k in combined for k in ["جنايات", "جنايه", "حدود", "قصاص", "ديات", "ديه", "تعزير", "عقوبات", "جرائم"]):
        return "الجنايات والحدود"
    elif any(k in combined for k in ["محاماه", "محامي", "تحكيم", "وساطه"]):
        return "المحاماة والتحكيم"
    elif any(k in combined for k in ["احوال شخصيه", "طلاق", "خلع", "فسخ", "نفقه", "حضانه"]):
        return "الأحوال الشخصية"
    elif any(k in combined for k in ["فرائض", "ميراث", "ارث", "مواريث", "تركه"]):
        return "الفرائض والمواريث"
    elif any(k in combined for k in ["حسبه", "محتسب", "مظالم"]):
        return "الحسبة والمظالم"
    elif any(k in combined for k in ["فقه مقارن", "مقارنه تشريعيه", "فقه قانوني", "فقه جنائي", "سياسه شرعيه"]):
        return "الفقه القانوني المقارن"
    elif any(k in combined for k in ["بحث", "دراسه", "رساله", "مقاله"]):
        return "أبحاث ودراسات قضائية"
    else:
        return "القضاء والأنظمة العامة"

def determine_material_type(title):
    """تحديد نوع المادة"""
    norm = normalize_arabic(title)
    if any(w in norm for w in ["شرح", "تشريح", "بيان", "ايضاح", "توضيح"]):
        return "شرح"
    elif any(w in norm for w in ["حاشيه", "تعليق", "تعليقات"]):
        return "حاشية"
    elif any(w in norm for w in ["بحث", "دراسه", "رساله", "اطروحه", "مقاله", "ورقه"]):
        return "بحث"
    elif any(w in norm for w in ["نظم", "منظومه", "الفيه", "قصيده"]):
        return "نظم"
    elif any(w in norm for w in ["فتوى", "فتاوى"]):
        return "فتوى"
    elif any(w in norm for w in ["نظام", "لائحه", "قانون"]):
        return "نظام"
    else:
        return "متن"

items = []
item_id = 1
seen_titles = set()

def add_item(title, author="", investigator="", link_telegram="", link_drive="", 
             link_direct="", source="", category="", material_type="", 
             file_type="PDF", file_size="", pages_count="", publisher="",
             year="", is_featured=False):
    global item_id
    
    title = clean(title)
    if not title or len(title) < 5:
        return
    
    # إزالة التكرار
    title_key = normalize_arabic(title)
    if title_key in seen_titles:
        return
    seen_titles.add(title_key)
    
    if not category:
        category = determine_category(title)
    if not material_type:
        material_type = determine_material_type(title)
    
    download_links_count = sum([1 for l in [link_telegram, link_drive, link_direct] if l])
    
    items.append({
        "id": f"qadaa_{item_id:04d}",
        "title": title,
        "author": clean(author),
        "investigator": clean(investigator),
        "publisher": clean(publisher),
        "year": clean(year),
        "link_telegram": clean(link_telegram),
        "link_drive": clean(link_drive),
        "link_direct": clean(link_direct),
        "source": source,
        "category": category,
        "material_type": material_type,
        "file_type": file_type,
        "file_size": clean(file_size),
        "pages_count": clean(pages_count),
        "is_featured": is_featured,
        "download_links_count": download_links_count
    })
    item_id += 1

# ==============================
# 1. المكتبة الوقفية (أفضل هيكل بيانات)
# ==============================
print("📂 معالجة المكتبة الوقفية...")
df = pd.read_excel(DATA_DIR / "waqfiya.xlsx", dtype=str).fillna("")
cols = list(df.columns)
# الأعمدة: رقم الكتاب، رابط، القسم الرئيسي، القسم الفرعي، الكتاب، المؤلف، المحقق، الناشر، تاريخ النشر، رقم الطبعة، حالة الفهرسة، مشاهدات، الصفحات، الأجزاء، الملفات، BIT، رابط التحميل

count_waqfiya = 0
for _, row in df.iterrows():
    title = clean(row.get("الكتاب", ""))
    section = clean(row.get("القسم الرئيسي", "")) + " " + clean(row.get("القسم الفرعي", ""))
    
    if not title:
        continue
    
    combined = title + " " + section
    if not (is_core_relevant(combined) or is_extended_relevant(combined)):
        continue
    
    # استبعاد "قضاء الحاجة" إذا لم يكن في سياق قضائي
    if "قضاء الحاجة" in title and "قضاء" not in section:
        continue
    
    link = clean(row.get("رابط التحميل", ""))
    if not link:
        link = extract_telegram_link(str(row.get(cols[1], "")))
    
    pages = clean(row.get("الصفحات", ""))
    
    # حساب حجم الملف من BIT
    bit_val = clean(row.get("BIT", ""))
    file_size = ""
    if bit_val and bit_val.replace(".", "").isdigit():
        size_mb = float(bit_val) / (1024*1024)
        if size_mb >= 1:
            file_size = f"{size_mb:.1f} MB"
        else:
            file_size = f"{float(bit_val)/1024:.1f} KB"
    
    add_item(
        title=title,
        author=clean(row.get("المؤلف", "")),
        investigator=clean(row.get("المحقق", "")),
        publisher=clean(row.get("الناشر", "")),
        year=clean(row.get("تاريخ النشر", "")),
        link_telegram=link,
        source="المكتبة الوقفية",
        category=determine_category(title, section),
        file_type="PDF",
        file_size=file_size,
        pages_count=pages,
        is_featured=clean(row.get("حالة الفهرسة", "")) == "مفهرس فهرسة كاملة"
    )
    count_waqfiya += 1

print(f"  ✅ {count_waqfiya} مادة من المكتبة الوقفية")

# ==============================
# 2. المكتبة الشاملة
# ==============================
print("📂 معالجة المكتبة الشاملة...")
df = pd.read_excel(DATA_DIR / "shamela.xlsx", dtype=str).fillna("")

count_shamela = 0
for _, row in df.iterrows():
    title = clean(row.get("الكتاب", ""))
    section = clean(row.get("القسم الرئيسي", "")) + " " + clean(row.get("القسم الفرعي", ""))
    
    if not title:
        continue
    
    combined = title + " " + section
    if not (is_core_relevant(combined) or is_extended_relevant(combined)):
        continue
    
    link = clean(row.get("رابط التحميل", ""))
    
    # حجم الملف من BIT
    bit_val = clean(row.get("BIT", ""))
    file_size = ""
    if bit_val and bit_val.replace(".", "").isdigit():
        size_mb = float(bit_val) / (1024*1024)
        if size_mb >= 1:
            file_size = f"{size_mb:.1f} MB"
        else:
            file_size = f"{float(bit_val)/1024:.1f} KB"
    
    death_year = clean(row.get("الوفاة هـ", ""))
    author_full = clean(row.get("المؤلف", ""))
    author_name = clean(row.get("الاسم", ""))
    author = author_name if author_name else author_full
    
    add_item(
        title=title,
        author=author,
        investigator=clean(row.get("المحقق", "")),
        publisher=clean(row.get("الناشر", "")),
        year=clean(row.get("تاريخ النشر", "")),
        link_telegram=link,
        source="المكتبة الشاملة",
        category=determine_category(title, section),
        file_type="EPUB",
        file_size=file_size,
    )
    count_shamela += 1

print(f"  ✅ {count_shamela} مادة من المكتبة الشاملة")

# ==============================
# 3. المكتبة العلمية
# ==============================
print("📂 معالجة المكتبة العلمية...")
df = pd.read_excel(DATA_DIR / "maktaba_ilmiya.xlsx", dtype=str).fillna("")
cols = list(df.columns)
# الأعمدة: رقم الكتاب، رابط، القسم الرئيسي، القسم الفرعي، الكتاب، المؤلف، ...

count_ilmiya = 0
for _, row in df.iterrows():
    # محاولة استخراج العنوان من العمود الصحيح
    title = ""
    author = ""
    section = ""
    link = ""
    pages = ""
    file_size = ""
    
    # تحليل الأعمدة المتاحة
    for col in cols:
        val = clean(str(row.get(col, "")))
        if col == "الكتاب" or (not title and len(val) > 10 and not val.startswith("http") and not val.startswith("ilmiya")):
            if not title:
                title = val
        elif "مؤلف" in col or "كاتب" in col:
            author = val
        elif "قسم" in col.lower() or "section" in col.lower():
            section += " " + val
        elif val.startswith("https://t.me"):
            link = val
    
    # إذا لم نجد العنوان، نحاول من الصف مباشرة
    if not title:
        row_vals = [clean(str(v)) for v in row.values]
        for v in row_vals:
            if len(v) > 10 and not v.startswith("http") and not v.startswith("ilmiya") and not v.replace(".", "").isdigit():
                title = v
                break
    
    if not title:
        continue
    
    combined = title + " " + section
    if not (is_core_relevant(combined) or is_extended_relevant(combined)):
        continue
    
    if not link:
        for v in row.values:
            v = str(v)
            if "t.me" in v:
                link = extract_telegram_link(v)
                break
    
    add_item(
        title=title,
        author=author,
        link_telegram=link,
        source="المكتبة العلمية",
        category=determine_category(title, section),
        file_type="PDF",
        file_size=file_size,
        pages_count=pages,
    )
    count_ilmiya += 1

print(f"  ✅ {count_ilmiya} مادة من المكتبة العلمية")

# ==============================
# 4. مكتبة الباحث العلمي (PDF)
# ==============================
print("📂 معالجة مكتبة الباحث العلمي (PDF)...")
df = pd.read_excel(DATA_DIR / "baheth_pdf.xlsx", dtype=str).fillna("")
cols = list(df.columns)
print(f"  الأعمدة: {cols}")

count_baheth_pdf = 0
for _, row in df.iterrows():
    title = clean(row.get("الكتاب", ""))
    section = clean(row.get("القسم", ""))
    author = ""
    link = ""
    
    if not title:
        # محاولة استخراج من الأعمدة الأخرى
        for col in cols:
            val = clean(str(row.get(col, "")))
            if len(val) > 10 and not val.startswith("http") and not val.startswith("bahith"):
                if not val.replace(".", "").replace(" ", "").isdigit():
                    title = val
                    break
    
    if not title:
        continue
    
    combined = title + " " + section
    if not (is_core_relevant(combined) or is_extended_relevant(combined)):
        continue
    
    # استخراج الرابط
    for v in row.values:
        v = str(v)
        if "t.me" in v:
            link = extract_telegram_link(v)
            break
    
    add_item(
        title=title,
        author=author,
        link_telegram=link,
        source="مكتبة الباحث العلمي",
        category=determine_category(title, section),
        file_type="PDF",
    )
    count_baheth_pdf += 1

print(f"  ✅ {count_baheth_pdf} مادة من مكتبة الباحث العلمي (PDF)")

# ==============================
# 5. مكتبة الباحث العلمي (Word)
# ==============================
print("📂 معالجة مكتبة الباحث العلمي (Word)...")
df = pd.read_excel(DATA_DIR / "baheth_word.xlsx", dtype=str).fillna("")
cols = list(df.columns)
print(f"  الأعمدة: {cols}")

count_baheth_word = 0
for _, row in df.iterrows():
    title = clean(row.get("الكتاب", ""))
    section = clean(row.get("القسم", ""))
    author = clean(row.get("المؤلف", ""))
    
    if not title:
        continue
    
    combined = title + " " + section
    if not (is_core_relevant(combined) or is_extended_relevant(combined)):
        continue
    
    link = ""
    for v in row.values:
        v = str(v)
        if "t.me" in v:
            link = extract_telegram_link(v)
            break
    
    add_item(
        title=title,
        author=author,
        link_telegram=link,
        source="مكتبة الباحث العلمي",
        category=determine_category(title, section),
        file_type="Word",
    )
    count_baheth_word += 1

print(f"  ✅ {count_baheth_word} مادة من مكتبة الباحث العلمي (Word)")

# ==============================
# 6. أبحاث البحوث (buhooth.link)
# ==============================
print("📂 معالجة أبحاث البحوث...")
df = pd.read_excel(DATA_DIR / "abhath.xlsx", sheet_name="جميع العناوين", dtype=str).fillna("")

# تحديد الصف الذي يحتوي على العناوين الفعلية
header_row = None
for i, row in df.iterrows():
    vals = [str(v) for v in row.values]
    if "الرقم" in vals or "العنوان" in vals:
        header_row = i
        break

if header_row is not None:
    df.columns = df.iloc[header_row]
    df = df.iloc[header_row+1:].reset_index(drop=True)

print(f"  الأعمدة بعد التحديد: {list(df.columns)}")

count_abhath = 0
for _, row in df.iterrows():
    # محاولة استخراج العنوان
    title = ""
    author = ""
    link = ""
    journal = ""
    
    for col in df.columns:
        val = clean(str(row.get(col, "")))
        col_str = str(col)
        if "عنوان" in col_str:
            title = val
        elif "مؤلف" in col_str or "مصدر" in col_str:
            author = val
        elif "رابط" in col_str:
            link = val
        elif "مجله" in normalize_arabic(col_str) or "مجلة" in col_str:
            journal = val
    
    if not title:
        continue
    
    if not (is_core_relevant(title) or is_extended_relevant(title)):
        continue
    
    add_item(
        title=title,
        author=author,
        link_direct=link,
        source=f"buhooth.link — {journal}" if journal else "buhooth.link",
        category=determine_category(title),
        material_type="بحث",
        file_type="PDF",
    )
    count_abhath += 1

print(f"  ✅ {count_abhath} مادة من أبحاث البحوث")

# ==============================
# إضافة مواد يدوية مميزة
# ==============================
print("\n📌 إضافة مواد مميزة يدوياً...")

featured_items = [
    {
        "title": "الطرق الحكمية في السياسة الشرعية",
        "author": "ابن قيم الجوزية",
        "source": "المكتبة الشاملة",
        "category": "القضاء الشرعي",
        "material_type": "متن",
        "is_featured": True,
        "file_type": "PDF",
    },
    {
        "title": "أعلام الموقعين عن رب العالمين",
        "author": "ابن قيم الجوزية",
        "source": "المكتبة الشاملة",
        "category": "القضاء الشرعي",
        "material_type": "متن",
        "is_featured": True,
        "file_type": "PDF",
    },
    {
        "title": "تبصرة الحكام في أصول الأقضية ومناهج الأحكام",
        "author": "ابن فرحون المالكي",
        "source": "المكتبة الوقفية",
        "category": "القضاء الشرعي",
        "material_type": "متن",
        "is_featured": True,
        "file_type": "PDF",
    },
    {
        "title": "المغني في فقه القضاء",
        "author": "ابن قدامة المقدسي",
        "source": "المكتبة الشاملة",
        "category": "القضاء الشرعي",
        "material_type": "متن",
        "is_featured": True,
        "file_type": "PDF",
    },
    {
        "title": "نظام الإجراءات الجزائية السعودي",
        "author": "المملكة العربية السعودية",
        "source": "الأنظمة السعودية",
        "category": "الأنظمة والتشريعات",
        "material_type": "نظام",
        "is_featured": True,
        "file_type": "PDF",
    },
    {
        "title": "نظام المرافعات الشرعية السعودي",
        "author": "المملكة العربية السعودية",
        "source": "الأنظمة السعودية",
        "category": "الأنظمة والتشريعات",
        "material_type": "نظام",
        "is_featured": True,
        "file_type": "PDF",
    },
    {
        "title": "نظام الأحوال الشخصية السعودي",
        "author": "المملكة العربية السعودية",
        "source": "الأنظمة السعودية",
        "category": "الأنظمة والتشريعات",
        "material_type": "نظام",
        "is_featured": True,
        "file_type": "PDF",
    },
    {
        "title": "أدب القاضي",
        "author": "الماوردي",
        "source": "المكتبة الوقفية",
        "category": "القضاء الشرعي",
        "material_type": "متن",
        "is_featured": True,
        "file_type": "PDF",
    },
    {
        "title": "الأحكام السلطانية والولايات الدينية",
        "author": "الماوردي",
        "source": "المكتبة الشاملة",
        "category": "القضاء الشرعي",
        "material_type": "متن",
        "is_featured": True,
        "file_type": "PDF",
    },
    {
        "title": "معين الحكام فيما يتردد بين الخصمين من الأحكام",
        "author": "علاء الدين الطرابلسي",
        "source": "المكتبة الشاملة",
        "category": "القضاء الشرعي",
        "material_type": "متن",
        "is_featured": True,
        "file_type": "PDF",
    },
]

for fi in featured_items:
    add_item(**fi)

print(f"  ✅ {len(featured_items)} مادة مميزة مضافة")

# ==============================
# الإحصاءات النهائية
# ==============================
print(f"\n{'='*50}")
print(f"📊 إجمالي المواد في المكنز: {len(items)}")

# إحصاء حسب القسم
from collections import Counter
cats = Counter(item["category"] for item in items)
print("\n📂 توزيع المواد حسب القسم:")
for cat, count in cats.most_common():
    print(f"  {cat}: {count}")

# إحصاء حسب المصدر
sources = Counter(item["source"] for item in items)
print("\n📚 توزيع المواد حسب المصدر:")
for src, count in sources.most_common():
    print(f"  {src}: {count}")

# إحصاء حسب نوع الملف
file_types = Counter(item["file_type"] for item in items)
print("\n📄 توزيع المواد حسب نوع الملف:")
for ft, count in file_types.most_common():
    print(f"  {ft}: {count}")

# حفظ الملف
output_path = OUTPUT_DIR / "items.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"\n✅ تم حفظ {len(items)} مادة في {output_path}")

# إنشاء ملف إحصاءات
stats = {
    "total_items": len(items),
    "categories": dict(cats.most_common()),
    "sources": dict(sources.most_common()),
    "file_types": dict(file_types.most_common()),
    "featured_count": sum(1 for item in items if item.get("is_featured")),
    "with_download_links": sum(1 for item in items if item.get("download_links_count", 0) > 0),
}

with open(OUTPUT_DIR / "stats.json", "w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

print(f"✅ تم حفظ الإحصاءات في stats.json")
