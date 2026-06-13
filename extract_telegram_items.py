#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
استخراج المواد من قناة تيليجرام "مفضلة اللجان شبه القضائية"
وإضافتها إلى items.json
"""

import json
import re
from pathlib import Path

UPLOAD_FILE = "/home/ubuntu/upload/result.json"
ITEMS_FILE = "/home/ubuntu/makanez-qadaa/items.json"

# قراءة الملف كنص خام ومعالجة أخطاء JSON
with open(UPLOAD_FILE, encoding="utf-8") as f:
    raw = f.read()

# محاولة إصلاح JSON المكسور بإزالة الأسطر المشكلة
# نستخدم regex لاستخراج البيانات مباشرة بدلاً من تحليل JSON

# استخراج أسماء الملفات وأحجامها
file_entries = re.findall(
    r'"file_name":\s*"([^"]+)"[^}]*"file_size":\s*(\d+)',
    raw
)

# استخراج النصوص مع مصادرها
text_entries = []
# نبحث عن كتل الرسائل
msg_pattern = re.finditer(
    r'"id":\s*(\d+)[^{]*?"type":\s*"message"[^{]*?"date":\s*"([^"]+)"'
    r'(?:[^{]*?"forwarded_from":\s*"([^"]*)")?'
    r'(?:[^{]*?"file_name":\s*"([^"]*)")?'
    r'(?:[^{]*?"file_size":\s*(\d+))?',
    raw, re.DOTALL
)

# استخراج جميع أسماء الملفات
all_file_names = re.findall(r'"file_name":\s*"([^"]+\.(?:pdf|PDF|doc|docx|xlsx|zip))"', raw)
all_file_sizes = re.findall(r'"file_size":\s*(\d+)', raw)

# استخراج النصوص (المحتوى النصي للرسائل)
# نبحث عن النمط: "text": "..." أو "text": [...]
text_pattern = re.findall(r'"text":\s*"([^"]{20,})"', raw)

# استخراج الروابط المباشرة
direct_links = re.findall(r'https?://(?!t\.me)[^\s"\\,\]]+\.pdf', raw)

print(f"📄 أسماء الملفات: {len(all_file_names)}")
print(f"🔗 روابط PDF مباشرة: {len(direct_links)}")
print(f"📝 نصوص: {len(text_pattern)}")

# بناء قاموس الملفات مع أحجامها
file_size_map = {}
size_idx = 0
for fname in all_file_names:
    if size_idx < len(all_file_sizes):
        file_size_map[fname] = int(all_file_sizes[size_idx])
        size_idx += 1

# ==============================
# تحديد القسم بناءً على اسم الملف
# ==============================
def get_category(name):
    n = name.lower()
    if any(k in n for k in ["جنائ", "جزائ", "جناي", "حدود", "قصاص", "دية", "تعزير", "عقوبات"]):
        return "الجنايات والحدود"
    elif any(k in n for k in ["تجاري", "شركات", "إفلاس", "افلاس", "تجارة"]):
        return "الأنظمة التجارية"
    elif any(k in n for k in ["إداري", "اداري", "مظالم", "ديوان"]):
        return "القضاء الإداري"
    elif any(k in n for k in ["تمييز", "استئناف", "عليا", "محكمة"]):
        return "المحاكم والمرافعات"
    elif any(k in n for k in ["مبادئ", "قرارات", "أحكام", "سوابق"]):
        return "المبادئ والقرارات القضائية"
    elif any(k in n for k in ["نظام", "أنظمة", "لائحة", "تشريع"]):
        return "الأنظمة والتشريعات"
    elif any(k in n for k in ["إثبات", "اثبات", "شهادة", "بينة"]):
        return "الإثبات والشهادة"
    elif any(k in n for k in ["تحكيم", "وساطة"]):
        return "المحاماة والتحكيم"
    elif any(k in n for k in ["وقف", "أوقاف", "تركة", "إرث", "ميراث"]):
        return "الفرائض والمواريث"
    elif any(k in n for k in ["عمل", "عمال", "موظف"]):
        return "أنظمة العمل"
    elif any(k in n for k in ["مرافعات", "إجراءات", "دعوى"]):
        return "المحاكم والمرافعات"
    elif any(k in n for k in ["محامي", "محاماة", "مستشار"]):
        return "المحاماة والتحكيم"
    elif any(k in n for k in ["تأمين", "مرور"]):
        return "الأنظمة والتشريعات"
    else:
        return "المبادئ والقرارات القضائية"

def format_size(bytes_val):
    if bytes_val > 1024*1024:
        return f"{bytes_val/(1024*1024):.1f} MB"
    elif bytes_val > 1024:
        return f"{bytes_val/1024:.1f} KB"
    return f"{bytes_val} B"

def clean_title(fname):
    """تنظيف اسم الملف ليصبح عنواناً"""
    title = fname
    # إزالة الامتداد
    title = re.sub(r'\.(pdf|PDF|doc|docx|xlsx|zip)$', '', title)
    # إزالة الشرطات السفلية
    title = title.replace('_', ' ')
    # إزالة الأرقام في البداية
    title = re.sub(r'^\d+[-\s]*', '', title)
    # تنظيف المسافات
    title = re.sub(r'\s+', ' ', title).strip()
    return title

# ==============================
# قراءة items.json الحالي
# ==============================
with open(ITEMS_FILE, encoding="utf-8") as f:
    items = json.load(f)

existing_count = len(items)
print(f"\n📊 عدد المواد الحالية: {existing_count}")

# الحصول على آخر ID
last_id = existing_count

# تتبع العناوين الموجودة لتجنب التكرار
def normalize(text):
    text = re.sub(r'[أإآا]', 'ا', text)
    text = re.sub(r'[\u064B-\u065F]', '', text)
    text = re.sub(r'ة', 'ه', text)
    return text.strip().lower()

seen_titles = {normalize(item["title"]) for item in items}

# ==============================
# إضافة الملفات من القناة
# ==============================
new_items = []

# القناة الرئيسية
CHANNEL_NAME = "مفضلة اللجان شبه القضائية"
CHANNEL_LINK = "https://t.me/+some_channel"  # سيُحدَّث لاحقاً

# قنوات المصادر المعروفة من الملف
SOURCE_CHANNELS = {
    "المستشارون السعوديون": "https://t.me/saudiattorneys",
    "المكتبة القانونية": "https://t.me/Ymtaz",
    "ألق للدورات القانونية": "https://t.me/AlaqPlatform",
    "منصة ألق الإلكترونية": "https://t.me/AlaqPlatform",
    "مدونة نظام المعاملات": "https://t.me/+some_channel",
    "مفضلة ناجز ومعين": "https://t.me/+some_channel",
    "دليل الأنظمة السعودية": "https://t.me/+some_channel",
}

added = 0
for fname in all_file_names:
    title = clean_title(fname)
    if len(title) < 5:
        continue
    
    title_norm = normalize(title)
    if title_norm in seen_titles:
        continue
    seen_titles.add(title_norm)
    
    last_id += 1
    size_bytes = file_size_map.get(fname, 0)
    file_size = format_size(size_bytes) if size_bytes > 0 else ""
    
    # تحديد نوع الملف
    ext = fname.split('.')[-1].lower() if '.' in fname else 'pdf'
    file_type_map = {'pdf': 'PDF', 'doc': 'Word', 'docx': 'Word', 'xlsx': 'Excel', 'zip': 'ZIP'}
    file_type = file_type_map.get(ext, 'PDF')
    
    new_items.append({
        "id": f"qadaa_{last_id:04d}",
        "title": title,
        "author": "",
        "investigator": "",
        "publisher": "",
        "year": "",
        "link_telegram": "",
        "link_drive": "",
        "link_direct": "",
        "source": CHANNEL_NAME,
        "category": get_category(fname),
        "material_type": "وثيقة قضائية",
        "file_type": file_type,
        "file_size": file_size,
        "pages_count": "",
        "is_featured": any(k in fname for k in ["مبادئ", "تمييز", "عليا", "دليل"]),
        "download_links_count": 0
    })
    added += 1

# إضافة روابط PDF المباشرة
for link in set(direct_links):
    # استخراج اسم الملف من الرابط
    fname = link.split('/')[-1]
    title = clean_title(fname)
    if len(title) < 5:
        continue
    
    title_norm = normalize(title)
    if title_norm in seen_titles:
        continue
    seen_titles.add(title_norm)
    
    last_id += 1
    new_items.append({
        "id": f"qadaa_{last_id:04d}",
        "title": title,
        "author": "وزارة العدل السعودية",
        "investigator": "",
        "publisher": "",
        "year": "",
        "link_telegram": "",
        "link_drive": "",
        "link_direct": link,
        "source": "وزارة العدل السعودية",
        "category": get_category(fname),
        "material_type": "وثيقة قضائية",
        "file_type": "PDF",
        "file_size": "",
        "pages_count": "",
        "is_featured": False,
        "download_links_count": 1
    })
    added += 1

print(f"✅ مواد جديدة من القناة: {added}")

# دمج المواد الجديدة
items.extend(new_items)

# حفظ الملف المحدث
with open(ITEMS_FILE, "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"📊 إجمالي المواد بعد الإضافة: {len(items)}")

# ==============================
# حفظ قائمة القنوات للمصادر
# ==============================
channels_info = {
    "main_channel": {
        "name": "مفضلة اللجان شبه القضائية",
        "description": "قناة تيليجرام متخصصة في اللجان شبه القضائية والمبادئ القضائية",
        "link": "https://t.me/+some_channel"
    },
    "forwarded_sources": [
        {"name": "المستشارون السعوديون ⚖️", "link": "https://t.me/saudiattorneys", "count": 72},
        {"name": "المكتبة القانونية", "link": "https://t.me/Ymtaz", "count": 11},
        {"name": "أصدقاء SaudiAttorneys", "link": "https://t.me/saudiattorneys", "count": 8},
        {"name": "ألق للدورات القانونية 🎧", "link": "https://t.me/AlaqPlatform", "count": 6},
        {"name": "مدونة نظام المعاملات ⚖️", "link": "https://t.me/+some_channel", "count": 4},
        {"name": "أنفوجرافيك و TV القانون", "link": "https://t.me/+some_channel", "count": 4},
        {"name": "⚖ ألق | وظائف القانون ⚖️", "link": "https://t.me/AlaqPlatform", "count": 3},
        {"name": "منصَّة ألق الإلكترونية", "link": "https://t.me/AlaqPlatform", "count": 2},
        {"name": "منصة المدرّب القانوني", "link": "https://t.me/+some_channel", "count": 2},
        {"name": "مفضلة ناجز ومعين", "link": "https://t.me/+some_channel", "count": 2},
        {"name": "مفضلة نظام التحكيم", "link": "https://t.me/+some_channel", "count": 1},
        {"name": "مفضلة المرافعات والإثبات", "link": "https://t.me/+some_channel", "count": 1},
        {"name": "مفضلة القضاء الإداري", "link": "https://t.me/+some_channel", "count": 1},
        {"name": "مفضلة أنظمة العمل ⚖️", "link": "https://t.me/+some_channel", "count": 1},
        {"name": "دليل الأنظمة السعودية", "link": "https://t.me/+some_channel", "count": 1},
        {"name": "⚖️ الأنظمة التجارية والمالية", "link": "https://t.me/+some_channel", "count": 1},
        {"name": "مفضلة الأنظمة الطبية", "link": "https://t.me/+some_channel", "count": 1},
        {"name": "مفضلة المرور والتأمين", "link": "https://t.me/+some_channel", "count": 1},
        {"name": "الموثق احمد المقبلي", "link": "https://t.me/+some_channel", "count": 1},
    ],
    "telegram_channels": [
        "https://t.me/saudiattorneys",
        "https://t.me/Ymtaz",
        "https://t.me/AlaqPlatform",
    ],
    "websites": [
        "https://ymtaz.sa",
        "https://qadha.org.sa",
        "https://sasl.sba.gov.sa",
        "https://www.moj.gov.sa",
    ]
}

with open("/home/ubuntu/makanez-qadaa/data/channels_info.json", "w", encoding="utf-8") as f:
    json.dump(channels_info, f, ensure_ascii=False, indent=2)

print("✅ تم حفظ معلومات القنوات في channels_info.json")

# تحديث الإحصاءات
from collections import Counter
cats = Counter(item["category"] for item in items)
sources = Counter(item["source"] for item in items)

stats = {
    "total_items": len(items),
    "categories": dict(cats.most_common()),
    "sources": dict(sources.most_common()),
    "featured_count": sum(1 for item in items if item.get("is_featured")),
    "with_download_links": sum(1 for item in items if item.get("download_links_count", 0) > 0),
    "telegram_channel": CHANNEL_NAME,
}

with open("/home/ubuntu/makanez-qadaa/stats.json", "w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

print(f"\n📊 الإحصاءات النهائية:")
print(f"  إجمالي المواد: {len(items):,}")
print(f"  المواد المميزة: {stats['featured_count']}")
for cat, count in cats.most_common(10):
    print(f"  {cat}: {count:,}")
