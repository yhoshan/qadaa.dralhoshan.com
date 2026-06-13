#!/usr/bin/env python3
"""استخراج مواد المكتبة القانونية من file_name وإضافتها لـ items.json"""

import json
import re
import os

# تحميل items.json الحالي (قبل الإضافة الخاطئة)
with open("/home/ubuntu/makanez-qadaa/items.json", "r", encoding="utf-8") as f:
    existing_items = json.load(f)

# إزالة أي مواد أُضيفت بالسكريبت السابق الخاطئ
existing_items = [item for item in existing_items if not item["id"].startswith("legal_lib_")]
print(f"المواد الحالية (بعد إزالة الإضافات الخاطئة): {len(existing_items)}")

# تحميل ملف تيليجرام
with open("/home/ubuntu/upload/result.json", "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(r',\s*}', '}', content)
content = re.sub(r',\s*]', ']', content)
data = json.loads(content)
messages = data.get("messages", [])
print(f"إجمالي الرسائل: {len(messages)}")

# اسم القناة
channel_name = data.get("name", "المكتبة القانونية")

def classify_item(title):
    t = title.lower()
    if any(w in t for w in ["نظام العمل", "عمال", "عامل", "عمالة", "توظيف", "أجور", "العمال", "العامل"]):
        return "أنظمة العمل"
    elif any(w in t for w in ["تجاري", "شركات", "شركة", "تجارة", "إفلاس", "إعسار", "الشيك", "الكمبيالة"]):
        return "الأنظمة التجارية"
    elif any(w in t for w in ["محاماة", "محامي", "محامون", "وكيل قضائي", "مكتب محاماة", "مهنة المحاماة", "المحامي"]):
        return "المحاماة والتحكيم"
    elif any(w in t for w in ["تحكيم", "وساطة", "تسوية نزاعات"]):
        return "المحاماة والتحكيم"
    elif any(w in t for w in ["إثبات", "شهادة", "بينة", "يمين", "اعتراف", "قرينة", "دليل", "الإثبات"]):
        return "الإثبات والشهادة"
    elif any(w in t for w in ["أحوال شخصية", "زواج", "طلاق", "نفقة", "حضانة", "فراق", "الأحوال الشخصية"]):
        return "الأحوال الشخصية"
    elif any(w in t for w in ["جناية", "جنائي", "جريمة", "عقوبة", "حد ", "قصاص", "دية", "قتل", "سرقة", "الجرائم", "الجريمة", "العقوبات"]):
        return "الجنايات والحدود"
    elif any(w in t for w in ["مرافعات", "محكمة", "قضاء", "قاضي", "حكم", "دعوى", "تقاضي", "استئناف", "تمييز", "المحاكم", "القضاء"]):
        return "المحاكم والمرافعات"
    elif any(w in t for w in ["إداري", "ديوان المظالم", "لجان", "هيئة", "الإداري"]):
        return "القضاء الإداري"
    elif any(w in t for w in ["نظام ", "لائحة ", "تنظيم", "قانون", "تشريع", "مرسوم", "الأنظمة"]):
        return "الأنظمة والتشريعات"
    elif any(w in t for w in ["بحث", "دراسة", "رسالة", "مقال", "ورقة"]):
        return "أبحاث ودراسات قضائية"
    else:
        return "القضاء والأنظمة العامة"

def get_material_type(title):
    t = title.lower()
    if any(w in t for w in ["نظام ", "لائحة ", "مرسوم ", "قرار "]):
        return "نظام"
    elif any(w in t for w in ["بحث", "دراسة", "رسالة", "مقال"]):
        return "بحث"
    elif any(w in t for w in ["شرح", "تعليق", "تفسير"]):
        return "شرح"
    else:
        return "كتاب"

def format_size(size_bytes):
    if not size_bytes:
        return ""
    try:
        size = int(size_bytes)
        if size > 1024*1024:
            return f"{size/(1024*1024):.1f} MB"
        elif size > 1024:
            return f"{size/1024:.0f} KB"
        return f"{size} B"
    except:
        return ""

# الحصول على العناوين الموجودة لتجنب التكرار
seen_titles = set(item["title"].strip() for item in existing_items)

new_items = []
start_id = len(existing_items) + 1

for msg in messages:
    if msg.get("type") != "message":
        continue
    
    file_name = msg.get("file_name", "")
    if not file_name:
        continue
    
    # استخراج العنوان من اسم الملف
    title = os.path.splitext(file_name)[0]
    title = title.replace("_", " ").strip()
    
    if not title or len(title) < 3:
        continue
    
    # تجنب التكرار
    if title in seen_titles:
        continue
    seen_titles.add(title)
    
    # نوع الملف
    file_ext = os.path.splitext(file_name)[1].upper().lstrip(".")
    if file_ext not in ["PDF", "MP3", "MP4", "DOCX", "DOC", "ZIP", "PPTX"]:
        file_ext = "PDF"
    
    # حجم الملف
    file_size = format_size(msg.get("file_size", ""))
    
    # رابط تيليجرام
    msg_id = msg.get("id", "")
    tg_link = f"https://t.me/iirmll/{msg_id}" if msg_id else ""
    
    # التصنيف
    category = classify_item(title)
    material_type = get_material_type(title)
    
    item_id = f"legal_lib_{start_id + len(new_items)}"
    
    new_items.append({
        "id": item_id,
        "title": title,
        "author": "",
        "investigator": "",
        "link_telegram": tg_link,
        "link_drive": "",
        "link_direct": "",
        "source": channel_name,
        "category": category,
        "material_type": material_type,
        "file_type": file_ext,
        "file_size": file_size,
        "pages_count": "",
        "is_featured": False,
        "download_links_count": 1 if tg_link else 0,
    })

print(f"مواد جديدة مستخرجة: {len(new_items)}")

# دمج المواد
all_items = existing_items + new_items

with open("/home/ubuntu/makanez-qadaa/items.json", "w", encoding="utf-8") as f:
    json.dump(all_items, f, ensure_ascii=False, indent=2)

print(f"إجمالي المواد بعد الدمج: {len(all_items)}")

# إحصاءات
from collections import Counter
cats = Counter(item["category"] for item in new_items)
print("\nتوزيع المواد الجديدة:")
for cat, count in cats.most_common():
    print(f"  {cat}: {count}")

# تحديث stats.json
stats = {
    "total": len(all_items),
    "with_download": sum(1 for item in all_items if item.get("download_links_count", 0) > 0),
    "categories": len(set(item["category"] for item in all_items)),
    "sources": len(set(item["source"] for item in all_items if item.get("source"))),
}
with open("/home/ubuntu/makanez-qadaa/stats.json", "w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)
print(f"\nالإحصاءات: {stats}")
