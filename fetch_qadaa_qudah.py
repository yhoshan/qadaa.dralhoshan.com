#!/usr/bin/env python3
"""استخراج مواد القضاء والقضاة من أرشيف الإنترنت مع استبعاد القضاء والقدر"""
import json, subprocess, time, re

def fetch_archive(query, rows=500):
    """استخراج نتائج من أرشيف الإنترنت"""
    import urllib.parse
    encoded = urllib.parse.quote(query)
    url = f"https://archive.org/advancedsearch.php?q={encoded}+AND+mediatype%3Atexts&fl[]=identifier&fl[]=title&fl[]=creator&fl[]=description&rows={rows}&output=json"
    result = subprocess.run(["curl", "-s", url], capture_output=True, text=True, timeout=90)
    data = json.loads(result.stdout)
    return data.get("response", {}).get("docs", [])

# كلمات الاستبعاد
NEGATIVE_WORDS = [
    "القضاء والقدر", "القدر والقضاء", "الإيمان بالقدر",
    "مسألة القدر", "عقيدة القضاء والقدر",
    "الجبر والاختيار", "قضاء الله وقدره",
    "رواية", "قصة قصيرة", "مسرحية", "ديوان شعر",
    "كرة القدم", "الرياضة البدنية",
    "الطب البشري", "الصيدلة", "الجيولوجيا",
    "دمروا الإسلام", "دمروا الاسلام",
    "القوانين الجاهلية", "اقرا اونلاين", "اقرأ اونلاين",
    "موسوعة الحضارة الاسلامية",
]

BAD_TITLE_PATTERNS = [
    r'^[a-z0-9_-]{1,15}$',  # معرّفات إنجليزية فقط
    r'^\d+$',               # أرقام فقط
    r'اقرا اونلاين',
    r'اقرأ اونلاين',
]

# كلمات إيجابية يجب أن تكون في العنوان
POSITIVE_TITLE_WORDS = [
    "القضاء", "القضاة", "القاضي", "المحكمة", "المحاكم",
    "الدعوى", "الأحكام القضائية", "الاجتهاد القضائي",
    "فقه القضاء", "أصول القضاء", "نظام القضاء",
    "إصلاح القضاء", "استقلال القضاء", "تاريخ القضاء",
    "القضاء الشرعي", "القضاء الإداري", "القضاء المدني",
    "القضاء الجنائي", "القضاء الدولي", "القضاء الدستوري",
    "القضاء في", "القضاء عند", "القضاء بين",
    "قضاء", "قضائي", "قضائية", "قضاة",
    "رجال القانون والقضاء", "وضع القضاء",
    "تطوير نظام القضاء", "منظومة القضاء",
]

def is_relevant(title, description=""):
    if isinstance(title, list): title = " ".join(title)
    if isinstance(description, list): description = " ".join(description)
    title_str = str(title)
    title_lower = title_str.lower()
    # فحص الأنماط السيئة في العنوان
    for pattern in BAD_TITLE_PATTERNS:
        if re.search(pattern, title_str.strip(), re.IGNORECASE):
            return False
    # استبعاد الكلمات السلبية في العنوان فقط
    for neg in NEGATIVE_WORDS:
        if neg in title_lower:
            return False
    # استبعاد "القضاء والقدر" بأشكال مختلفة
    if re.search(r'القضاء\s+والقدر|القدر\s+والقضاء|قضاء\s+الله\s+وقدر', title_lower):
        return False
    # استبعاد "القضاء على" بمعنى الإنهاء (تاريخي وليس قضائياً)
    if re.search(r'القضاء\s+على\s+', title_lower):
        return False
    # استبعاد المواد التاريخية غير القضائية
    historical_non_legal = [
        "صلاح الدين الأيوبي", "الدولة الفاطمية", "الدولة العثمانية",
        "الدولة الأموية", "الدولة العباسية",
        "طرائق وأساليب المماليك", "الثورات في مصر",
        "تحرير بيت المقدس", "الفتح الإسلامي",
        "جهوده في القضاء", "وجهوده في القضاء",
        "الحياة في عصر", "في حياة بعض الادباء",
    ]
    for hist in historical_non_legal:
        if hist in title_lower:
            return False
    # يجب أن يحتوي العنوان على كلمة إيجابية
    for pos in POSITIVE_TITLE_WORDS:
        if pos in title_lower:
            return True
    return False

def clean_title(title):
    if isinstance(title, list): title = title[0] if title else ""
    title = str(title)
    title = re.sub(r'\s*(Pdf|PDF|pdf)\s*(كتاب|File|file)?\s*\d*', '', title)
    title = re.sub(r'\s*(File|file)\s*(كتاب)?\s*\d*', '', title)
    title = re.sub(r'^\d+\s+', '', title)
    return title.strip()

def get_category(title):
    t = title.lower()
    if any(w in t for w in ["قضاة", "القاضي", "أدب القاضي", "ولاية القضاء", "تاريخ القضاء"]):
        return "القضاء الشرعي"
    elif any(w in t for w in ["إداري", "مجلس الدولة", "دستوري", "إداري"]):
        return "القضاء الإداري"
    elif any(w in t for w in ["جنائي", "جنايات", "عقوبات", "جريمة", "حدود"]):
        return "الجنايات والحدود"
    elif any(w in t for w in ["مدني", "تجاري", "عقود", "مرافعات"]):
        return "الإجراءات القضائية"
    elif any(w in t for w in ["فقه القضاء", "أصول القضاء", "القضاء في الإسلام", "القضاء الشرعي"]):
        return "القضاء الشرعي"
    else:
        return "القضاء الشرعي"

def build_item(doc):
    identifier = doc.get("identifier", "")
    title = clean_title(doc.get("title", ""))
    creator = doc.get("creator", "")
    if isinstance(creator, list):
        creator = creator[0] if creator else ""
    return {
        "id": f"archive_{identifier}",
        "title": title,
        "author": creator,
        "investigator": "",
        "publisher": "أرشيف الإنترنت",
        "year": "",
        "link_telegram": "",
        "link_drive": "",
        "link_direct": f"https://archive.org/download/{identifier}/{identifier}.pdf",
        "source": "أرشيف الإنترنت",
        "category": get_category(title),
        "material_type": "كتاب",
        "file_type": "PDF",
        "file_size": "",
        "pages_count": "",
        "is_featured": False,
        "download_links_count": 1
    }

# استخراج من مصادر متعددة
queries = [
    ("القضاء", 500),
    ("القضاة", 300),
    ("فقه القضاء", 200),
    ("القضاء الشرعي", 200),
    ("القضاء الإداري", 200),
]

all_docs = {}
for query, rows in queries:
    print(f"🔍 استخراج: {query}...")
    docs = fetch_archive(query, rows)
    print(f"  → {len(docs)} نتيجة")
    for doc in docs:
        identifier = doc.get("identifier", "")
        if identifier:
            all_docs[identifier] = doc
    time.sleep(1)

print(f"\nإجمالي بعد إزالة التكرار: {len(all_docs)}")

# تصفية
filtered = []
for identifier, doc in all_docs.items():
    title = doc.get("title", "")
    description = str(doc.get("description", ""))
    if is_relevant(title, description):
        filtered.append(build_item(doc))

print(f"بعد التصفية: {len(filtered)} مادة")

# عرض عينة
print("\nعينة من المواد:")
for item in filtered[:20]:
    print(f"  [{item['category']}] {item['title'][:70]}")

# حفظ
with open("/home/ubuntu/makanez-qadaa/archive_qadaa_new.json", "w", encoding="utf-8") as f:
    json.dump(filtered, f, ensure_ascii=False, indent=2)

print(f"\n✅ تم حفظ {len(filtered)} مادة في archive_qadaa_new.json")
