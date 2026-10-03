#!/usr/bin/env python3
"""Build a conservative, auditable candidate set from مكتبة القاضي محمد الأهدل.
The script does not alter the catalogue. It excludes politics, non-legal works,
unnamed files, and exact duplicates within the source or current catalogue.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path('/home/ubuntu/makanez-qadaa')
EXPORT = Path('/home/ubuntu/upload/pasted_file_6vW7UQ_result.json')
ITEMS = ROOT / 'items.json'
RAW_OUT = ROOT / 'qadi_ahdal_2026-10-03_raw_inventory.json'
CANDIDATES_OUT = ROOT / 'qadi_ahdal_2026-10-03_candidates.json'
EXCLUDED_OUT = ROOT / 'qadi_ahdal_2026-10-03_excluded.json'
PRECHECK_OUT = ROOT / 'qadi_ahdal_2026-10-03_precheck.json'

CONTROL = re.compile(r'[\u200e\u200f\u202a-\u202e\u2066-\u2069]')
DIACRITICS = re.compile(r'[\u064B-\u065F\u0670\u06D6-\u06ED]')
# Scope instruction from the user: exclude any political or factional material.
POLITICAL = re.compile(
    r'الحوث|انصار الله|أنصار الله|حزب الله|حزب |الأحزاب|حزب|سياس(?:ة|ي)|'
    r'انتخاب|برلمان|مجلس النواب|رئيس الجمهوري|ثورة|انقلاب|دبلوماس|'
    r'المؤتمر الشعبي|البعث|الإخوان|الميليش|مليشيا|جماعة مسلحة|حرب|'
    r'حماس|داعش|القاعدة|تنظيم الدولة|جبهة النصرة|غزة|فلسطين|إسرائيل|اسرائيل|الاحتلال',
    re.IGNORECASE,
)
LEGAL = re.compile(
    r'قانون|نظام|لائحة|تشريع|قضائ|محكم|حكم قضائي|حكم المحكمة|أحكام قضائية|'
    r'مبادئ قضائية|دعوى|دعاوى|قاض|'
    r'مرافعات|تنفيذ|إثبات|نيابة|تحقيق|جنائ|جريمة|عقوب|جرائم|'
    r'محام|محاماة|عقد|عقود|التزام|مدني|تجاري|شركة|شركات|إفلاس|'
    r'تحكيم|وساطة|إداري|دستور(?!ي سياسي)|ضريبة|جمارك|مصرف|تمويل|'
    r'تأمين|ملكية فكرية|حقوق المؤلف|علامات تجارية|براءة اختراع|'
    r'سجل تجاري|سجل عقاري|منافسات|مشتريات|استملاك|وقف شرعي|'
    r'أحوال شخصية|طلاق|زواج|تركة|مواريث|وصية|طب شرعي|'
    r'علم الاجرام|علم العقاب|طب شرعي|قانوني|عدلي|قانونية|قضائية|'
    r'اتفاقية|معاهدة|قواعد دولية|قانون دولي|مجلة الحقوق|مجلة القانون|'
    r'هيئة قضائية|سلطة قضائية|مهنة المحاماة|الوثائق|التوثيق',
    re.IGNORECASE,
)
NONLEGAL_STRONG = re.compile(
    r'رواية|ديوان|شعر|قصة|قصص|السيرة الذاتية|مذكرات (?!قانون)|'
    r'تفسير|آيات الاحكام|القرآن|الحديث|العقيدة|التوحيد|فقه (?!القضاء|المعاملات|الجنايات)|'
    r'أصول الفقه|اللغة|النحو|البلاغة|التاريخ (?!القضائي)|جغرافيا|'
    r'طب(?! شرعي)|هندسة|زراعة|كيمياء|فيزياء|رياضيات|طبخ|'
    r'تربية|تعليم(?! العالي|القانوني)|إدارة (?!قضائية|قانونية)|'
    r'اقتصاد(?!ي قانوني| وقانوني)|تنمية بشرية|فلسفة (?!القانون|العقوبة)|'
    r'تصوف|أدب',
    re.IGNORECASE,
)
DOC_MIMES = {
    'application/pdf': 'PDF',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word',
    'application/msword': 'Word',
}
INCOMPLETE_TOKENS = {
    'في', 'من', 'عن', 'على', 'إلى', 'الى', 'لـ', 'ل', 'القسم', 'الجزء',
    'المجلد', 'جرائم', 'دراسة', 'بحث', 'قانون', 'نظام', 'لائحة', 'شرح',
    'الد', 'الـ', 'ال', 'ج', 'ق', 'ف', 'ب',
}


def text_value(message: dict) -> str:
    value = message.get('text', '')
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return ' '.join(x if isinstance(x, str) else str(x.get('text', '')) for x in value)
    return ''


def clean_title(value: str) -> str:
    value = unicodedata.normalize('NFKC', value or '')
    value = CONTROL.sub('', value)
    value = re.sub(r'\.(?:pdf|docx?|epub|zip|rar|7z|pptx?)$', '', value, flags=re.I)
    value = value.replace('_', ' ')
    value = re.sub(r'\s+', ' ', value).strip(' .-_–—')
    return value


def normalize(value: str) -> str:
    value = clean_title(value)
    value = DIACRITICS.sub('', value)
    value = value.translate(str.maketrans('أإآٱىةؤئ', 'اااايهوي'))
    value = re.sub(r'[^\w\s]', ' ', value, flags=re.UNICODE)
    return re.sub(r'\s+', ' ', value).strip().lower()


def file_size_label(size: int | None) -> str:
    if not size:
        return ''
    return f'{size / (1024 * 1024):.1f} MB'


def descriptive(title: str) -> bool:
    compact = re.sub(r'[^\u0621-\u064Aa-zA-Z]', '', title)
    # Numeric-only, filenames, and ultra-short fragments cannot be safely catalogued.
    return len(compact) >= 7 and bool(re.search(r'[\u0621-\u064A]', compact))


def incomplete_title(title: str) -> bool:
    tokens = re.findall(r'[\u0621-\u064A]+|[A-Za-z]+', title)
    return bool(tokens) and tokens[-1].lower() in INCOMPLETE_TOKENS


def classify(title: str) -> tuple[str, str]:
    if re.search(r'مجلة|دورية', title): return 'الدراسات القانونية', 'مجلة'
    if re.search(r'أحكام|مبادئ|سوابق|نقض|تمييز|محكمة|قضائ', title): return 'القضاء والأحكام والإجراءات', 'أحكام'
    if re.search(r'شرح|تعليق|وجيز|مدخل|نظرية|دليل|ملخص|فقه القضاء', title): return 'الدراسات القانونية', 'شرح'
    if re.search(r'لائحة|قرار|تعميم', title): return 'الأنظمة والقانون العام', 'لائحة' if 'لائحة' in title else 'قرار'
    if re.search(r'قانون|نظام|تشريع', title):
        if re.search(r'جنائ|جريمة|عقوب|مخدر|سجن|إجرام', title): return 'القانون الجنائي', 'نظام'
        if re.search(r'تجاري|شركة|إفلاس|مصرف|تمويل|تأمين|ضريبة|جمارك|منافسات|مشتريات', title): return 'القانون التجاري والمالي', 'نظام'
        if re.search(r'مدني|عقد|التزام|عقار|إيجار|ملكية|استهلاك', title): return 'القانون المدني والعقاري', 'نظام'
        if re.search(r'دولي|اتفاقية|معاهدة', title): return 'القانون الدولي والمقارن', 'اتفاقية دولية' if re.search(r'اتفاقية|معاهدة', title) else 'نظام'
        if re.search(r'دستور|إداري|دولة|وظيف', title): return 'القانون الإداري والدستوري', 'نظام'
        if re.search(r'أحوال شخصية|تركة|وصية|زواج|طلاق|مواريث', title): return 'الأحوال الشخصية والتركات', 'نظام'
        return 'الأنظمة والقانون العام', 'نظام'
    if re.search(r'محام|مرافعة|مذكرة|صياغة|دفاع', title): return 'المحاماة والصياغة القانونية', 'دليل إجرائي'
    if re.search(r'تحكيم|وساطة', title): return 'القانون الدولي والمقارن', 'قواعد دولية'
    if re.search(r'رسالة|أطروحة|دراسة|بحث', title): return 'الدراسات القانونية', 'بحث'
    if re.search(r'ملكية فكرية|مؤلف|علامة تجارية|براءة', title): return 'الملكية الفكرية', 'مادة قانونية'
    return 'الدراسات القانونية', 'كتاب'


def main() -> None:
    data = json.loads(EXPORT.read_text(encoding='utf8'))
    current = json.loads(ITEMS.read_text(encoding='utf8'))
    existing_ids = {str(x.get('id', '')) for x in current}
    existing_title_keys = {normalize(str(x.get('title', ''))) for x in current if normalize(str(x.get('title', '')))}

    raw = []
    for message in data.get('messages', []):
        mime = message.get('mime_type', '')
        if message.get('type') != 'message' or mime not in DOC_MIMES or not message.get('file_name'):
            continue
        title = clean_title(str(message['file_name']))
        raw.append({
            'post_id': int(message['id']),
            'id': f'qadi_ahdal_{int(message["id"])}',
            'title': title,
            'context': clean_title(text_value(message))[:600],
            'date': str(message.get('date', '')),
            'file_name': str(message['file_name']),
            'file_size_bytes': message.get('file_size'),
            'file_type': DOC_MIMES[mime],
            'telegram_url': f'https://t.me/Ahdal_Legal_Lib/{int(message["id"])}',
        })
    if len({x['id'] for x in raw}) != len(raw): raise AssertionError('duplicated post IDs')
    RAW_OUT.write_text(json.dumps(raw, ensure_ascii=False, indent=2)+'\n',encoding='utf8')

    candidates, excluded = [], []
    source_seen: dict[str, str] = {}
    for record in raw:
        combined = f"{record['title']} {record['context']}"
        key = normalize(record['title'])
        if not descriptive(record['title']):
            excluded.append({**record,'reason':'اسم ملف غير وصفي أو رقمي ولا يمكن فهرسته بثقة.'}); continue
        if incomplete_title(record['title']):
            excluded.append({**record,'reason':'العنوان مبتور أو غير مكتمل؛ لا يمكن فهرسته ببيان موثوق.'}); continue
        if POLITICAL.search(combined):
            excluded.append({**record,'reason':'استبعاد سياسي صريح وفق قرار المستخدم.'}); continue
        if not LEGAL.search(combined):
            excluded.append({**record,'reason':'لا تظهر صلة قانونية أو قضائية كافية في العنوان أو سياقه.'}); continue
        # Nonlegal content is out unless the title also carries a stronger legal subject.
        if NONLEGAL_STRONG.search(combined) and not LEGAL.search(record['title']):
            excluded.append({**record,'reason':'موضوع عام/ديني/أدبي أو غير قانوني وفق العنوان والسياق.'}); continue
        if record['id'] in existing_ids:
            excluded.append({**record,'reason':'المعرّف موجود في المكنز.'}); continue
        if key in existing_title_keys:
            excluded.append({**record,'reason':'عنوان مطابق بعد التطبيع لسجل قائم؛ منع تكرار مؤكد.'}); continue
        if key in source_seen:
            excluded.append({**record,'reason':f'تكرار مطابق داخل المصدر؛ أبقيت {source_seen[key]} فقط.'}); continue
        source_seen[key] = record['id']
        category, material_type = classify(record['title'])
        candidates.append({
            'id': record['id'], 'title': record['title'], 'author': 'مكتبة القاضي محمد الأهدل',
            'investigator':'', 'publisher':'', 'year':record['date'][:4],
            'link_telegram':record['telegram_url'], 'link_drive':'', 'link_direct':'',
            'source':'مكتبة القاضي محمد الأهدل القانونية والقضائية', 'category':category,
            'material_type':material_type, 'file_type':record['file_type'],
            'file_size':file_size_label(record['file_size_bytes']), 'pages_count':'',
            'is_featured':False, 'download_links_count':1,
        })
    candidate_ids = [x['id'] for x in candidates]
    assert len(candidate_ids)==len(set(candidate_ids))
    assert not set(candidate_ids)&existing_ids
    assert not any(normalize(x['title']) in existing_title_keys for x in candidates)
    CANDIDATES_OUT.write_text(json.dumps(candidates,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    EXCLUDED_OUT.write_text(json.dumps(excluded,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    summary = {
        'source_name':data.get('name'), 'source_type':data.get('type'), 'source_id':data.get('id'),
        'supported_document_records':len(raw), 'accepted_candidates':len(candidates), 'excluded_records':len(excluded),
        'exclusions_by_reason':dict(Counter(x['reason'] for x in excluded)),
        'accepted_by_file_type':dict(Counter(x['file_type'] for x in candidates)),
        'accepted_by_category':dict(Counter(x['category'] for x in candidates)),
        'accepted_by_material_type':dict(Counter(x['material_type'] for x in candidates)),
        'items_before_count':len(current), 'items_before_sha256':hashlib.sha256(ITEMS.read_bytes()).hexdigest(),
        'candidate_ids_sha256':hashlib.sha256('\n'.join(candidate_ids).encode()).hexdigest(),
        'checks':{'candidate_ids_unique':len(candidate_ids)==len(set(candidate_ids)), 'no_existing_id_overlap':not bool(set(candidate_ids)&existing_ids), 'no_exact_normalized_title_overlap':not any(normalize(x['title']) in existing_title_keys for x in candidates)},
    }
    PRECHECK_OUT.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
