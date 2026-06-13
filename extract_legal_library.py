#!/usr/bin/env python3
"""استخراج مواد المكتبة القانونية وإضافتها لـ items.json"""

import json
import re
import os

# تحميل items.json الحالي
with open("/home/ubuntu/makanez-qadaa/items.json", "r", encoding="utf-8") as f:
    existing_items = json.load(f)

print(f"المواد الحالية: {len(existing_items)}")

# تحميل ملف تيليجرام
with open("/home/ubuntu/upload/result.json", "r", encoding="utf-8") as f:
    content = f.read()

# تنظيف JSON
content = re.sub(r',\s*}', '}', content)
content = re.sub(r',\s*]', ']', content)

try:
    data = json.loads(content)
except:
    # محاولة إصلاح الملف
    lines = content.split('\n')
    fixed_lines = []
    for line in lines:
        fixed_lines.append(line)
    content = '\n'.join(fixed_lines)
    data = json.loads(content)

messages = data.get("messages", [])
print(f"إجمالي الرسائل: {len(messages)}")

# الحصول على أعلى ID موجود
max_id = max((int(item["id"].replace("legal_lib_", "").replace("qadaa_", "").replace("rasail_", "").replace("tg_", "").replace("item_", "")) 
              for item in existing_items 
              if item["id"].split("_")[-1].isdigit()), default=0)

# تصنيف المواد
def classify_item(title, text=""):
    combined = (title + " " + text).lower()
    
    if any(w in combined for w in ["نظام العمل", "عمال", "عامل", "عمالة", "توظيف", "أجور", "إجازة عمل"]):
        return "أنظمة العمل"
    elif any(w in combined for w in ["نظام التجارة", "تجاري", "شركات", "عقد تجاري", "تجارة إلكترونية", "إفلاس"]):
        return "الأنظمة التجارية"
    elif any(w in combined for w in ["محاماة", "محامي", "محامون", "وكيل قضائي", "مكتب محاماة", "مهنة المحاماة"]):
        return "المحاماة والتحكيم"
    elif any(w in combined for w in ["تحكيم", "وساطة", "تسوية نزاعات"]):
        return "المحاماة والتحكيم"
    elif any(w in combined for w in ["إثبات", "شهادة", "بينة", "يمين", "اعتراف", "قرينة", "دليل"]):
        return "الإثبات والشهادة"
    elif any(w in combined for w in ["أحوال شخصية", "زواج", "طلاق", "نفقة", "حضانة", "ميراث", "وصية", "فراق"]):
        return "الأحوال الشخصية"
    elif any(w in combined for w in ["جناية", "جنائي", "جريمة", "عقوبة", "حد", "قصاص", "دية", "قتل", "سرقة", "زنا"]):
        return "الجنايات والحدود"
    elif any(w in combined for w in ["مرافعات", "محكمة", "قضاء", "قاضي", "حكم", "دعوى", "تقاضي", "استئناف", "تمييز"]):
        return "المحاكم والمرافعات"
    elif any(w in combined for w in ["إداري", "ديوان المظالم", "لجان", "هيئة", "وزارة", "حكومة"]):
        return "القضاء الإداري"
    elif any(w in combined for w in ["نظام", "لائحة", "تنظيم", "قانون", "تشريع", "مرسوم"]):
        return "الأنظمة والتشريعات"
    elif any(w in combined for w in ["بحث", "دراسة", "رسالة", "مقال", "ورقة"]):
        return "أبحاث ودراسات قضائية"
    else:
        return "القضاء والأنظمة العامة"

def get_material_type(title, text=""):
    combined = (title + " " + text).lower()
    if any(w in combined for w in ["نظام ", "لائحة ", "مرسوم ", "قرار "]):
        return "نظام"
    elif any(w in combined for w in ["بحث", "دراسة", "رسالة", "مقال"]):
        return "بحث"
    elif any(w in combined for w in ["شرح", "تعليق", "تفسير"]):
        return "شرح"
    else:
        return "كتاب"

# استخراج الروابط
def extract_links(msg):
    text = msg.get("text", "")
    if isinstance(text, list):
        parts = []
        for part in text:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict):
                parts.append(part.get("text", ""))
        text = " ".join(parts)
    
    links = re.findall(r'https?://[^\s\)\]"\']+', text)
    tg_links = [l for l in links if "t.me" in l]
    direct_links = [l for l in links if "t.me" not in l and any(ext in l.lower() for ext in [".pdf", ".doc", ".mp3", ".mp4", "drive.google", "archive.org"])]
    
    return tg_links[0] if tg_links else None, direct_links[0] if direct_links else None

# استخراج المواد
new_items = []
seen_titles = set(item["title"].strip() for item in existing_items)

for msg in messages:
    if msg.get("type") != "message":
        continue
    
    file_name = msg.get("file", "")
    if not file_name:
        # محاولة من media_type
        media_type = msg.get("media_type", "")
        if media_type not in ["document", "audio", "video"]:
            continue
    
    # استخراج العنوان
    title = ""
    if file_name:
        title = os.path.splitext(os.path.basename(file_name))[0]
        title = title.replace("_", " ").strip()
    
    if not title:
        text = msg.get("text", "")
        if isinstance(text, list):
            parts = []
            for part in text:
                if isinstance(part, str):
                    parts.append(part)
                elif isinstance(part, dict):
                    parts.append(part.get("text", ""))
            text = " ".join(parts)
        # أخذ أول سطر كعنوان
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines:
            title = lines[0][:100]
    
    if not title or len(title) < 3:
        continue
    
    # تجنب التكرار
    if title in seen_titles:
        continue
    seen_titles.add(title)
    
    # نوع الملف
    file_ext = os.path.splitext(file_name)[1].upper().lstrip(".") if file_name else "PDF"
    if not file_ext:
        file_ext = "PDF"
    
    # الروابط
    tg_link, direct_link = extract_links(msg)
    
    # رابط تيليجرام من message_id
    msg_id = msg.get("id", "")
    channel_username = "althomali2"  # القناة الرئيسية
    if not tg_link and msg_id:
        tg_link = f"https://t.me/{channel_username}/{msg_id}"
    
    # التصنيف
    category = classify_item(title)
    material_type = get_material_type(title)
    
    item_id = f"legal_lib_{len(existing_items) + len(new_items) + 1}"
    
    new_items.append({
        "id": item_id,
        "title": title,
        "author": "",
        "investigator": "",
        "link_telegram": tg_link or "",
        "link_drive": "",
        "link_direct": direct_link or "",
        "source": "المكتبة القانونية",
        "category": category,
        "material_type": material_type,
        "file_type": file_ext if file_ext in ["PDF", "MP3", "MP4", "DOCX", "DOC", "ZIP"] else "PDF",
        "file_size": "",
        "pages_count": "",
        "is_featured": False,
        "download_links_count": 1 if (tg_link or direct_link) else 0,
    })

print(f"مواد جديدة مستخرجة: {len(new_items)}")

# دمج المواد
all_items = existing_items + new_items

# إعادة ترقيم
for i, item in enumerate(all_items, 1):
    pass  # الحفاظ على IDs الأصلية

with open("/home/ubuntu/makanez-qadaa/items.json", "w", encoding="utf-8") as f:
    json.dump(all_items, f, ensure_ascii=False, indent=2)

print(f"إجمالي المواد بعد الدمج: {len(all_items)}")

# إحصاءات
from collections import Counter
cats = Counter(item["category"] for item in new_items)
print("\nتوزيع المواد الجديدة:")
for cat, count in cats.most_common():
    print(f"  {cat}: {count}")
