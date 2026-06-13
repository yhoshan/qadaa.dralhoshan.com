#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
استخراج مواد مكنز القضاء والأنظمة والمحاماة من فهارس Google Drive
"""

import pandas as pd
import json
import re
import os
from pathlib import Path

DATA_DIR = Path("/home/ubuntu/makanez-qadaa/data")

# الكلمات المفتاحية لموضوع القضاء والأنظمة والمحاماة
KEYWORDS = [
    # القضاء الفقهي
    "قضاء", "قضائي", "قضائية", "القضاء", "القاضي", "القضاة", "الحكم", "الأحكام القضائية",
    "الشهادة", "الشهادات", "الإثبات", "الدعوى", "الدعاوى", "المرافعات",
    "الحدود", "القصاص", "الديات", "الدية", "التعزير",
    "الإقرار", "البينة", "اليمين", "الحلف", "الأيمان",
    "الخصومة", "التقاضي", "الفصل في الخصومات",
    # الأنظمة والقانون
    "نظام", "أنظمة", "النظام", "الأنظمة", "قانون", "قانوني", "قانونية",
    "تشريع", "تشريعات", "التشريع", "لائحة", "لوائح", "اللوائح",
    "نظام الأحوال الشخصية", "نظام المرافعات", "نظام الإجراءات الجزائية",
    "نظام العمل", "نظام التجارة", "نظام الشركات",
    "الأنظمة السعودية", "المملكة العربية السعودية",
    "الفقه القانوني", "الفقه الجنائي",
    # المحاماة والمحاكم
    "محاماة", "المحاماة", "محامي", "محامٍ", "المحامي",
    "محكمة", "المحكمة", "المحاكم", "محاكم",
    "قضية", "قضايا", "حكم قضائي", "أحكام",
    "المحكمة العليا", "ديوان المظالم", "المحكمة الإدارية",
    "المحكمة الجزائية", "المحكمة التجارية",
    # الجنايات والعقوبات
    "جناية", "جنايات", "الجنايات", "جريمة", "جرائم", "الجرائم",
    "عقوبة", "عقوبات", "العقوبات", "الحدود الشرعية",
    "الجزاء", "العقوبة الشرعية", "الفقه الجنائي",
    # الفقه المتعلق بالقضاء
    "أدب القاضي", "آداب القضاء", "ولاية القضاء",
    "الشهود", "تزكية الشهود", "الجرح والتعديل في الشهادة",
    "الحكم بالقرائن", "القرائن القضائية",
    "التحكيم", "الوساطة", "الصلح",
    # الفقه الإداري والمالي
    "الفقه الإداري", "الإدارة القضائية",
    "المال العام", "بيت المال", "الوقف",
    "الحسبة", "المحتسب", "ولاية الحسبة",
    "المظالم", "ولاية المظالم", "ديوان المظالم",
    # الأحوال الشخصية
    "الأحوال الشخصية", "الطلاق", "الخلع", "الفسخ",
    "النفقة", "الحضانة", "الولاية", "الوصاية",
    "الميراث", "الإرث", "الفرائض", "التركة",
    # الفقه المقارن والتطبيقي
    "الفقه المقارن", "المقارنة التشريعية",
    "الفقه التطبيقي", "الفتاوى القضائية",
    "الاجتهاد القضائي", "الاجتهاد في القضاء",
]

# كلمات الاستبعاد (لتجنب المواد غير ذات الصلة)
EXCLUDE_KEYWORDS = [
    "قضاء الحاجة",  # قضاء الحاجة بمعنى دورة المياه
    "قضاء الصلاة",  # قضاء الصلاة الفائتة فقط إذا لم يكن في سياق قضائي
]

def normalize_arabic(text):
    """تطبيع النص العربي لتسهيل البحث"""
    if not isinstance(text, str):
        return ""
    # توحيد الهمزات
    text = re.sub(r'[أإآا]', 'ا', text)
    # إزالة التشكيل
    text = re.sub(r'[\u064B-\u065F]', '', text)
    # توحيد التاء المربوطة والهاء
    text = re.sub(r'ة', 'ه', text)
    return text.strip()

def is_relevant(text):
    """فحص إذا كان النص يتعلق بموضوع القضاء والأنظمة والمحاماة"""
    if not isinstance(text, str):
        return False
    
    normalized = normalize_arabic(text.lower())
    
    # فحص الاستبعاد أولاً
    for excl in EXCLUDE_KEYWORDS:
        excl_norm = normalize_arabic(excl.lower())
        if excl_norm in normalized and not any(normalize_arabic(k.lower()) in normalized for k in [
            "قضاء", "قضائي", "قضائية", "القضاء", "القاضي", "القضاة"
        ] if normalize_arabic(k.lower()) != normalize_arabic("قضاء")):
            pass  # لا نستبعد إذا كان السياق قضائياً
    
    # فحص الكلمات المفتاحية
    for kw in KEYWORDS:
        kw_norm = normalize_arabic(kw.lower())
        if kw_norm in normalized:
            return True
    return False

def extract_from_excel(filepath, source_name):
    """استخراج البيانات من ملف Excel"""
    results = []
    try:
        xl = pd.ExcelFile(filepath)
        print(f"\n📂 {source_name}: {len(xl.sheet_names)} ورقة")
        
        for sheet_name in xl.sheet_names:
            try:
                df = pd.read_excel(filepath, sheet_name=sheet_name, dtype=str)
                df = df.fillna("")
                
                print(f"  📄 {sheet_name}: {len(df)} صف، أعمدة: {list(df.columns[:5])}")
                
                for idx, row in df.iterrows():
                    # دمج كل الأعمدة النصية للبحث
                    all_text = " ".join([str(v) for v in row.values if isinstance(v, str)])
                    
                    if is_relevant(all_text):
                        results.append({
                            "source": source_name,
                            "sheet": sheet_name,
                            "row_data": dict(row),
                            "raw_text": all_text[:500]
                        })
            except Exception as e:
                print(f"  ⚠️ خطأ في ورقة {sheet_name}: {e}")
    except Exception as e:
        print(f"❌ خطأ في {filepath}: {e}")
    
    return results

# استخراج من جميع المصادر
all_results = []

sources = [
    (DATA_DIR / "maktaba_ilmiya.xlsx", "المكتبة العلمية"),
    (DATA_DIR / "baheth_pdf.xlsx", "مكتبة الباحث العلمي (PDF)"),
    (DATA_DIR / "baheth_word.xlsx", "مكتبة الباحث العلمي (Word)"),
    (DATA_DIR / "abhath.xlsx", "أبحاث البحوث"),
    (DATA_DIR / "waqfiya.xlsx", "المكتبة الوقفية"),
    (DATA_DIR / "shamela.xlsx", "المكتبة الشاملة"),
]

for filepath, source_name in sources:
    if filepath.exists():
        results = extract_from_excel(filepath, source_name)
        all_results.extend(results)
        print(f"  ✅ وُجد {len(results)} مادة ذات صلة")
    else:
        print(f"⚠️ الملف غير موجود: {filepath}")

print(f"\n📊 إجمالي المواد المستخرجة: {len(all_results)}")

# حفظ النتائج الخام
with open(DATA_DIR / "raw_results.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)

print(f"✅ تم حفظ النتائج الخام في raw_results.json")

# عرض عينة من النتائج
print("\n--- عينة من النتائج ---")
for r in all_results[:5]:
    print(f"المصدر: {r['source']} | الورقة: {r['sheet']}")
    print(f"النص: {r['raw_text'][:200]}")
    print("---")
