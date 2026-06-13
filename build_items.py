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

def normalize_arabic(text):
    """تطبيع النص العربي"""
    if not isinstance(text, str):
        return ""
    text = re.sub(r'[أإآا]', 'ا', text)
    text = re.sub(r'[\u064B-\u065F]', '', text)
    return text.strip()

def clean_text(text):
    """تنظيف النص"""
    if not isinstance(text, str) or text in ["nan", "None", ""]:
        return ""
    return text.strip()

def extract_telegram_link(text):
    """استخراج رابط تيليجرام من النص"""
    if not isinstance(text, str):
        return ""
    match = re.search(r'https://t\.me/\S+', text)
    return match.group(0) if match else ""

def extract_drive_link(text):
    """استخراج رابط Google Drive من النص"""
    if not isinstance(text, str):
        return ""
    match = re.search(r'https://drive\.google\.com/\S+', text)
    return match.group(0) if match else ""

def determine_category(title, section=""):
    """تحديد القسم بناءً على العنوان"""
    title_norm = normalize_arabic(title.lower())
    section_norm = normalize_arabic(section.lower())
    combined = title_norm + " " + section_norm
    
    categories = {
        "القضاء الشرعي": ["قضاء", "قاضي", "قضاه", "اداب القضاء", "ولايه القضاء", "احكام القضاء"],
        "الأنظمة والتشريعات": ["نظام", "انظمه", "تشريع", "لائحه", "لوائح", "قانون", "قانوني"],
        "المحاكم والمرافعات": ["محكمه", "محاكم", "مرافعات", "اجراءات", "تقاضي", "دعوى", "دعاوى"],
        "الإثبات والشهادة": ["اثبات", "شهاده", "شهود", "بينه", "يمين", "اقرار", "قرائن"],
        "الجنايات والحدود": ["جنايات", "جنايه", "حدود", "قصاص", "ديات", "ديه", "تعزير", "عقوبات", "عقوبه", "جرائم", "جريمه"],
        "المحاماة والتحكيم": ["محاماه", "محامي", "تحكيم", "وساطه", "صلح"],
        "الأحوال الشخصية": ["احوال شخصيه", "طلاق", "خلع", "فسخ", "نفقه", "حضانه", "ولايه", "وصايه"],
        "الفرائض والمواريث": ["فرائض", "ميراث", "ارث", "مواريث", "تركه"],
        "الحسبة والمظالم": ["حسبه", "محتسب", "مظالم", "ديوان المظالم"],
        "الفقه القانوني المقارن": ["فقه مقارن", "مقارنه تشريعيه", "فقه قانوني", "فقه جنائي"],
        "أبحاث ودراسات قضائية": ["بحث", "دراسه", "رساله", "اطروحه", "مقاله"],
    }
    
    for cat, keywords in categories.items():
        for kw in keywords:
            if kw in combined:
                return cat
    
    return "القضاء والأنظمة العامة"

def determine_material_type(title, section=""):
    """تحديد نوع المادة"""
    title_lower = title.lower()
    combined = title_lower + " " + section.lower()
    
    if any(w in combined for w in ["شرح", "تشريح", "بيان", "إيضاح", "توضيح"]):
        return "شرح"
    elif any(w in combined for w in ["حاشية", "تعليق", "تعليقات", "ملاحظات"]):
        return "حاشية"
    elif any(w in combined for w in ["بحث", "دراسة", "رسالة", "أطروحة", "مقالة", "ورقة"]):
        return "بحث"
    elif any(w in combined for w in ["نظم", "منظومة", "ألفية", "قصيدة"]):
        return "نظم"
    elif any(w in combined for w in ["فتوى", "فتاوى"]):
        return "فتوى"
    elif any(w in combined for w in ["نظام", "لائحة", "قانون"]):
        return "نظام"
    else:
        return "متن"

# ==============================
# معالجة المكتبة العلمية
# ==============================
print("📂 معالجة المكتبة العلمية...")
df_ilmiya = pd.read_excel(DATA_DIR / "maktaba_ilmiya.xlsx", dtype=str).fillna("")
print(f"  الأعمدة: {list(df_ilmiya.columns)}")
print(f"  عينة:\n{df_ilmiya.head(2).to_string()}")

# ==============================
# معالجة مكتبة الباحث PDF
# ==============================
print("\n📂 معالجة مكتبة الباحث العلمي (PDF)...")
df_baheth_pdf = pd.read_excel(DATA_DIR / "baheth_pdf.xlsx", dtype=str).fillna("")
print(f"  الأعمدة: {list(df_baheth_pdf.columns)}")
print(f"  عينة:\n{df_baheth_pdf.head(2).to_string()}")

# ==============================
# معالجة مكتبة الباحث Word
# ==============================
print("\n📂 معالجة مكتبة الباحث العلمي (Word)...")
df_baheth_word = pd.read_excel(DATA_DIR / "baheth_word.xlsx", dtype=str).fillna("")
print(f"  الأعمدة: {list(df_baheth_word.columns)}")
print(f"  عينة:\n{df_baheth_word.head(2).to_string()}")

# ==============================
# معالجة أبحاث البحوث
# ==============================
print("\n📂 معالجة أبحاث البحوث...")
df_abhath = pd.read_excel(DATA_DIR / "abhath.xlsx", sheet_name="جميع العناوين", dtype=str).fillna("")
print(f"  الأعمدة: {list(df_abhath.columns)}")
print(f"  عينة:\n{df_abhath.head(3).to_string()}")

# ==============================
# معالجة المكتبة الوقفية
# ==============================
print("\n📂 معالجة المكتبة الوقفية...")
df_waqfiya = pd.read_excel(DATA_DIR / "waqfiya.xlsx", dtype=str).fillna("")
print(f"  الأعمدة: {list(df_waqfiya.columns)}")
print(f"  عينة:\n{df_waqfiya.head(2).to_string()}")

# ==============================
# معالجة المكتبة الشاملة
# ==============================
print("\n📂 معالجة المكتبة الشاملة...")
df_shamela = pd.read_excel(DATA_DIR / "shamela.xlsx", dtype=str).fillna("")
print(f"  الأعمدة: {list(df_shamela.columns)}")
print(f"  عينة:\n{df_shamela.head(2).to_string()}")
