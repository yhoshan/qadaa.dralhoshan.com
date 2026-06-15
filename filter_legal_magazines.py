#!/usr/bin/env python3
"""
تصفية مواد قناة "مجلات وصحف قانونية" (LegalMagazinesandNewspapers)
معرف القناة: 2265085799
"""
import json
import re
import uuid

# كلمات مفتاحية مرتبطة بالقضاء والأنظمة والمحاماة
INCLUDE_KEYWORDS = [
    # قضاء وقانون
    'قضاء', 'قضائي', 'قضائية', 'قاضي', 'قضاة', 'محكمة', 'محاكم', 'تقاضي',
    'قانون', 'قانوني', 'قانونية', 'تشريع', 'تشريعي', 'نظام', 'أنظمة',
    'حكم', 'أحكام', 'قرار', 'قرارات', 'حكومي',
    # محاماة ومرافعات
    'محامي', 'محاماة', 'مرافعة', 'مرافعات', 'وكالة', 'وكيل',
    'دعوى', 'دعاوى', 'خصومة', 'تقاضي', 'إجراءات',
    # عقود ومعاملات
    'عقد', 'عقود', 'تعاقد', 'التزام', 'التزامات', 'مسؤولية',
    'تعويض', 'ضرر', 'تعويضات', 'إثراء',
    # تحكيم
    'تحكيم', 'محكّم', 'محكمين', 'تسوية', 'وساطة',
    # جنائي وجزائي
    'جنائي', 'جنائية', 'جزائي', 'جزائية', 'جريمة', 'جرائم',
    'عقوبة', 'عقوبات', 'جزاء', 'حبس', 'سجن',
    # حقوق
    'حقوق', 'حق', 'ملكية', 'ملكية فكرية',
    # مجلات قانونية
    'مجلة الحقوق', 'مجلة القانون', 'مجلة المحامي', 'مجلة العدل',
    'مجلة التحكيم', 'مجلة الفقه', 'مجلة الدراسات القانونية',
    'مجلة البحوث القانونية', 'مجلة الشريعة والقانون',
    'مجلة المحقق الحلي', 'مجلة روح القوانين',
    'مجلة البحوث والدراسات القضائية',
    # كلمات عامة
    'فقه', 'شريعة', 'إسلامي', 'مقارن', 'مقارنة',
    'دستور', 'دستوري', 'دستورية', 'برلمان',
    'إداري', 'إدارية', 'إدارة',
    'مدني', 'مدنية', 'تجاري', 'تجارية',
    'دولي', 'دولية',
    'وزارة العدل', 'المكتب الفني',
    'نزاع', 'نزاعات', 'منازعة', 'منازعات',
    'سيبراني', 'معلوماتي', 'إلكتروني',
    'اجراء', 'إجراء', 'اجراءات', 'إجراءات',
    'استئناف', 'نقض', 'تمييز',
    'وقف', 'ميراث', 'أحوال شخصية',
    'عمالي', 'عمل', 'عمال',
]

# كلمات استبعاد صريحة
EXCLUDE_KEYWORDS = [
    'مقاطعة', 'بضائع مقاطعة', 'إسرائيل', 'صهيوني',
    'سياسي', 'سياسية', 'انتخاب', 'انتخابات',
    'رياضة', 'رياضي', 'كرة', 'فريق',
    'طبي', 'طبية', 'صحة', 'دواء', 'دوائي',
    'أدبي', 'أدبية', 'شعر', 'رواية', 'قصة',
    'اقتصاد', 'اقتصادي', 'مالي', 'مالية', 'بنك', 'بنوك',
    'تسجيل دخول', 'مستخدم جديد',
    'تطبيق', 'برنامج',
    'وعي', 'تشاركي', 'مبادرة',
    'شبكة المنصات', 'LDPNetwork',
    'ظاهرة تغريب أسماء',
    'مركز الدعم الإلكتروني',
]

def normalize_arabic(text):
    """تطبيع النص العربي"""
    text = re.sub(r'[أإآا]', 'ا', text)
    text = re.sub(r'[ةه]', 'ه', text)
    text = re.sub(r'[يى]', 'ي', text)
    return text

def is_legal_content(text):
    """تحديد هل المحتوى قانوني/قضائي"""
    if not text or len(text) < 10:
        return False
    
    text_norm = normalize_arabic(text.lower())
    
    # استبعاد صريح أولاً
    for kw in EXCLUDE_KEYWORDS:
        if normalize_arabic(kw.lower()) in text_norm:
            return False
    
    # تضمين إذا وُجدت كلمة مفتاحية
    for kw in INCLUDE_KEYWORDS:
        if normalize_arabic(kw.lower()) in text_norm:
            return True
    
    return False

def categorize(text):
    """تصنيف المادة"""
    text_lower = text.lower()
    
    if any(kw in text_lower for kw in ['تحكيم', 'محكّم', 'محكمين']):
        return 'تحكيم'
    elif any(kw in text_lower for kw in ['محامي', 'محاماة', 'مرافعة', 'مرافعات']):
        return 'محاماة'
    elif any(kw in text_lower for kw in ['جنائي', 'جزائي', 'جريمة', 'جرائم', 'عقوبة']):
        return 'قانون جنائي'
    elif any(kw in text_lower for kw in ['دستور', 'دستوري', 'برلمان', 'تشريع']):
        return 'قانون دستوري'
    elif any(kw in text_lower for kw in ['إداري', 'إدارية', 'إدارة']):
        return 'قانون إداري'
    elif any(kw in text_lower for kw in ['عقد', 'عقود', 'مدني', 'مدنية', 'التزام']):
        return 'قانون مدني'
    elif any(kw in text_lower for kw in ['تجاري', 'تجارية', 'شركة', 'شركات']):
        return 'قانون تجاري'
    elif any(kw in text_lower for kw in ['قضاء', 'قضائي', 'قاضي', 'قضاة', 'محكمة']):
        return 'قضاء'
    elif any(kw in text_lower for kw in ['نظام', 'أنظمة', 'لائحة', 'تنظيم']):
        return 'أنظمة'
    else:
        return 'دراسات قانونية'

def extract_title(text):
    """استخراج عنوان من النص"""
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines:
        return None
    
    # أول سطر غير فارغ وغير رمز
    for line in lines:
        line = re.sub(r'^[📔⚖📚🗃📲#@\s]+', '', line).strip()
        if len(line) > 10 and not line.startswith('http'):
            return line[:200]
    return None

def main():
    with open('/home/ubuntu/makanez-qadaa/result_legal_magazines.json') as f:
        data = json.load(f)
    
    messages = data.get('messages', [])
    channel_id = str(data.get('id', '2265085799'))
    
    new_items = []
    skipped = 0
    
    for m in messages:
        if m.get('type') != 'message':
            continue
        
        # استخراج النص
        text = m.get('text', '')
        if isinstance(text, list):
            full = ' '.join([t if isinstance(t, str) else t.get('text', '') for t in text])
        else:
            full = text
        full = full.strip()
        
        # يجب أن يكون هناك ملف
        f = m.get('file', '')
        if not f:
            skipped += 1
            continue
        
        # فحص المحتوى القانوني
        if not is_legal_content(full):
            skipped += 1
            continue
        
        msg_id = m.get('id')
        link_tg = f'https://t.me/c/{channel_id}/{msg_id}'
        
        title = extract_title(full)
        if not title:
            # استخدام أول 100 حرف من النص
            title = full[:100].replace('\n', ' ').strip()
        
        category = categorize(full)
        
        # تحديد نوع المادة
        if 'مجلة' in full:
            material_type = 'بحث'
        elif 'كتاب' in full or 'مؤلف' in full:
            material_type = 'كتاب'
        else:
            material_type = 'بحث'
        
        item = {
            'id': f'legal_mag_{msg_id}',
            'title': title,
            'author': '',
            'investigator': '',
            'link_telegram': link_tg,
            'link_drive': '',
            'link_direct': '',
            'source': 'قناة المجلات والصحف القانونية',
            'category': category,
            'material_type': material_type,
            'file_type': 'PDF',
            'file_size': '',
            'pages_count': '',
            'is_featured': False,
            'download_links_count': 1,
            'description': full[:300] if len(full) > 50 else ''
        }
        
        new_items.append(item)
    
    print(f'مواد قانونية مصفاة: {len(new_items)}')
    print(f'مواد مستبعدة: {skipped}')
    
    # عرض عينة
    print('\n--- عينة من المواد المضافة ---')
    for item in new_items[:20]:
        print(f'  [{item["category"]}] {item["title"][:80]}')
        print(f'  {item["link_telegram"]}')
        print()
    
    # حفظ النتيجة
    with open('/home/ubuntu/makanez-qadaa/new_legal_magazines_items.json', 'w', encoding='utf-8') as f:
        json.dump(new_items, f, ensure_ascii=False, indent=2)
    
    print(f'\nتم حفظ {len(new_items)} مادة في new_legal_magazines_items.json')
    return new_items

if __name__ == '__main__':
    main()
