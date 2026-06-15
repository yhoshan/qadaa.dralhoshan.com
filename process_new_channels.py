#!/usr/bin/env python3
"""
معالجة وإضافة مواد قناتي:
1. great_law - المكتبة القانونية الكبرى
2. muath_alyahya - تسهيل الأنظمة
"""
import json
import re
import os

def get_text(m):
    text = m.get('text', '')
    if isinstance(text, list):
        parts = []
        for t in text:
            if isinstance(t, dict):
                parts.append(t.get('text', ''))
            else:
                parts.append(str(t))
        return ''.join(parts)
    return str(text)

def normalize_arabic(text):
    """تطبيع النص العربي"""
    text = re.sub(r'[أإآا]', 'ا', text)
    text = re.sub(r'[ىي]', 'ي', text)
    text = re.sub(r'ة', 'ه', text)
    return text

def clean_title(text):
    """تنظيف العنوان"""
    # إزالة الإيموجي
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
    text = re.sub(r'[\u2600-\u27BF]', '', text)
    # إزالة mentions
    text = re.sub(r'@\w+', '', text)
    # إزالة الهاشتاق
    text = re.sub(r'#\S+', '', text)
    # إزالة الروابط
    text = re.sub(r'https?://\S+', '', text)
    # تنظيف المسافات
    text = re.sub(r'\s+', ' ', text).strip()
    # إزالة الشرطات والنقاط في البداية
    text = re.sub(r'^[-–—.،:]+\s*', '', text).strip()
    return text

def detect_category(text):
    """تحديد التصنيف بناءً على النص"""
    text_norm = normalize_arabic(text.lower())
    
    if any(kw in text_norm for kw in ['محام', 'محاماه', 'وكيل', 'نقابه']):
        return 'المحاماة'
    elif any(kw in text_norm for kw in ['نظام', 'لائحه', 'مرسوم', 'قرار', 'تشريع', 'تنظيم']):
        return 'الأنظمة واللوائح'
    elif any(kw in text_norm for kw in ['قضاء', 'قضائي', 'محكمه', 'قاضي', 'قضاه', 'دعوى', 'مرافعه', 'احكام', 'حكم']):
        return 'القضاء'
    elif any(kw in text_norm for kw in ['جريمه', 'جرائم', 'عقوبه', 'جنائي', 'جنايه', 'جنحه']):
        return 'القانون الجنائي'
    elif any(kw in text_norm for kw in ['عقد', 'عقود', 'التزام', 'مدني', 'تجاري', 'شركه', 'ملكيه']):
        return 'القانون المدني والتجاري'
    elif any(kw in text_norm for kw in ['دستور', 'دستوري', 'حقوق الانسان', 'حريات']):
        return 'القانون الدستوري'
    elif any(kw in text_norm for kw in ['دولي', 'دوليه', 'معاهده', 'اتفاقيه']):
        return 'القانون الدولي'
    elif any(kw in text_norm for kw in ['اداري', 'اداريه', 'اداره']):
        return 'القانون الإداري'
    elif any(kw in text_norm for kw in ['رساله', 'اطروحه', 'ماجستير', 'دكتوراه', 'بحث', 'دراسه']):
        return 'الأبحاث والرسائل'
    else:
        return 'عام'

def detect_material_type(text):
    """تحديد نوع المادة"""
    text_lower = text.lower()
    if any(kw in text_lower for kw in ['رسالة', 'أطروحة', 'ماجستير', 'دكتوراه']):
        return 'رسالة علمية'
    elif any(kw in text_lower for kw in ['بحث', 'دراسة', 'مقال', 'ورقة']):
        return 'بحث'
    elif any(kw in text_lower for kw in ['نظام', 'لائحة', 'مرسوم', 'قرار']):
        return 'نظام'
    elif any(kw in text_lower for kw in ['شرح', 'تفسير', 'تعليق']):
        return 'شرح'
    elif any(kw in text_lower for kw in ['ملخص', 'مختصر', 'موجز']):
        return 'ملخص'
    elif any(kw in text_lower for kw in ['كتاب', 'مؤلف', 'موسوعة', 'معجم']):
        return 'كتاب'
    else:
        return 'مادة قانونية'

# ==========================================
# معالجة قناة great_law
# ==========================================
print("=" * 60)
print("معالجة قناة @great_law - المكتبة القانونية الكبرى")
print("=" * 60)

# تحميل البيانات المصفاة المحفوظة مسبقاً
with open('/home/ubuntu/great_law_filtered.json', 'r', encoding='utf-8') as f:
    great_law_filtered = json.load(f)

# الكلمات المفتاحية القانونية المرتبطة بالمكنز
legal_keywords = [
    'قضاء', 'قضائي', 'محكمة', 'محاكم', 'قاضي', 'قضاة',
    'محامي', 'محاماة', 'وكيل', 'مرافعة', 'مرافعات',
    'نظام', 'أنظمة', 'لائحة', 'لوائح', 'تشريع', 'تشريعات',
    'قانون', 'قانوني', 'قانونية', 'تقنين',
    'عقد', 'عقود', 'التزام', 'التزامات',
    'جريمة', 'جرائم', 'عقوبة', 'عقوبات', 'جنائي', 'جنائية',
    'إجراءات', 'دعوى', 'دعاوى', 'حكم', 'أحكام',
    'إثبات', 'تنفيذ', 'طعن', 'استئناف', 'تمييز',
    'حقوق', 'مسؤولية', 'شركة', 'شركات', 'تجاري',
    'ملكية', 'عقار', 'إيجار', 'إداري', 'إدارية',
    'دستور', 'دستوري', 'دولي', 'دولية', 'معاهدة',
    'بحث', 'دراسة', 'رسالة', 'أطروحة', 'فقه', 'شريعة',
    'ماجستير', 'دكتوراه', 'موسوعة', 'معجم',
]

# كلمات الاستبعاد
exclude_keywords = [
    'رواية', 'روايات', 'أدب', 'شعر', 'قصة', 'قصص',
    'طبخ', 'وصفة', 'طب', 'صحة', 'رياضة', 'كرة',
    'ديني', 'إسلامي', 'قرآن', 'حديث', 'فقه إسلامي',
]

# تصفية وبناء items من great_law
great_law_items = []
seen_titles = set()

for item in great_law_filtered:
    text = item['text']
    clean = clean_title(text)
    
    if len(clean) < 8:
        continue
    
    # تجاهل المكررات
    title_key = normalize_arabic(clean[:40])
    if title_key in seen_titles:
        continue
    
    # تجاهل الرسائل التي تبدو إعلانات أو روابط فقط
    if clean.startswith('http') or clean.startswith('www'):
        continue
    
    # تجاهل الرسائل القصيرة جداً التي لا تحمل عنواناً
    if len(clean) < 10:
        continue
    
    seen_titles.add(title_key)
    
    category = detect_category(clean)
    material_type = detect_material_type(clean)
    
    great_law_items.append({
        "id": f"great_law_{item['id']}",
        "title": clean,
        "author": "",
        "investigator": "",
        "link_telegram": item['link'],
        "link_drive": "",
        "link_direct": "",
        "source": "المكتبة القانونية الكبرى",
        "category": category,
        "material_type": material_type,
        "file_type": "PDF",
        "file_size": "",
        "pages_count": "",
        "is_featured": False,
        "download_links_count": 1
    })

print(f"مواد great_law بعد التصفية: {len(great_law_items)}")

# ==========================================
# معالجة قناة muath_alyahya - تسهيل الأنظمة
# ==========================================
print("\n" + "=" * 60)
print("معالجة قناة @muath_alyahya - تسهيل الأنظمة")
print("=" * 60)

with open('/home/ubuntu/upload/result.json', 'r', encoding='utf-8') as f:
    muath_data = json.load(f)

muath_msgs = muath_data.get('messages', [])
muath_items = []
seen_muath = set()

for m in muath_msgs:
    if m.get('type') != 'message':
        continue
    
    text = get_text(m).strip()
    if not text or len(text) < 15:
        continue
    
    clean = clean_title(text)
    if len(clean) < 10:
        continue
    
    # تجاهل المكررات
    title_key = normalize_arabic(clean[:40])
    if title_key in seen_muath:
        continue
    
    seen_muath.add(title_key)
    
    # تحديد العنوان (أول سطر)
    lines = [l.strip() for l in clean.split('\n') if l.strip()]
    title = lines[0] if lines else clean
    if len(title) > 120:
        title = title[:120] + '...'
    
    category = detect_category(clean)
    material_type = detect_material_type(clean)
    
    # تحديد نوع الملف - معظمها مقالات ونصوص
    file_type = "مقال"
    if '(File not included' in str(m.get('file', '')):
        file_type = "PDF"
    
    muath_items.append({
        "id": f"muath_{m['id']}",
        "title": title,
        "author": "م. معاذ اليحيى",
        "investigator": "",
        "link_telegram": f"https://t.me/muath_alyahya/{m['id']}",
        "link_drive": "",
        "link_direct": "",
        "source": "تسهيل الأنظمة",
        "category": category,
        "material_type": material_type,
        "file_type": file_type,
        "file_size": "",
        "pages_count": "",
        "is_featured": False,
        "download_links_count": 1
    })

print(f"مواد تسهيل الأنظمة: {len(muath_items)}")

# ==========================================
# دمج مع items.json الحالي
# ==========================================
print("\n" + "=" * 60)
print("دمج مع items.json الحالي")
print("=" * 60)

with open('/home/ubuntu/makanez-qadaa/items.json', 'r', encoding='utf-8') as f:
    current_items = json.load(f)

print(f"المواد الحالية: {len(current_items)}")

# فحص التكرار مع المواد الحالية
existing_links = set()
for item in current_items:
    for field in ['link_telegram', 'link_direct', 'link_drive']:
        val = item.get(field, '')
        if val:
            existing_links.add(val)

# إضافة great_law
added_great_law = 0
for item in great_law_items:
    if item['link_telegram'] not in existing_links:
        current_items.append(item)
        existing_links.add(item['link_telegram'])
        added_great_law += 1

# إضافة muath_alyahya
added_muath = 0
for item in muath_items:
    if item['link_telegram'] not in existing_links:
        current_items.append(item)
        existing_links.add(item['link_telegram'])
        added_muath += 1

print(f"مضاف من great_law: {added_great_law}")
print(f"مضاف من تسهيل الأنظمة: {added_muath}")
print(f"الإجمالي الجديد: {len(current_items)}")

# حفظ items.json
with open('/home/ubuntu/makanez-qadaa/items.json', 'w', encoding='utf-8') as f:
    json.dump(current_items, f, ensure_ascii=False, indent=2)

print("\nتم حفظ items.json")

# ==========================================
# تحديث stats.json
# ==========================================
total = len(current_items)

# حساب الإحصاءات
qadaa_count = sum(1 for i in current_items if 'قضاء' in i.get('category', '') or 'قضائي' in i.get('category', ''))
nizam_count = sum(1 for i in current_items if 'نظام' in i.get('category', '') or 'لائحة' in i.get('category', '') or 'تشريع' in i.get('category', ''))
mohama_count = sum(1 for i in current_items if 'محاماة' in i.get('category', '') or 'محامي' in i.get('category', ''))
other_count = total - qadaa_count - nizam_count - mohama_count

stats = {
    "total_items": total,
    "qadaa_count": qadaa_count,
    "nizam_count": nizam_count,
    "mohama_count": mohama_count,
    "other_count": max(0, other_count),
    "books_count": total,
    "audio_count": 0,
    "video_count": 0,
    "size_gb": round(total * 0.012, 1),
    "last_updated": "2026-06-15"
}

with open('/home/ubuntu/makanez-qadaa/client/public/stats.json', 'w', encoding='utf-8') as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

print(f"\nتم تحديث stats.json:")
print(f"  الإجمالي: {total}")
print(f"  القضاء: {qadaa_count}")
print(f"  الأنظمة: {nizam_count}")
print(f"  المحاماة: {mohama_count}")
print(f"  أخرى: {other_count}")
