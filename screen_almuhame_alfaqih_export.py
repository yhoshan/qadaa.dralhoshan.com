#!/usr/bin/env python3
"""Conservative, read-only screening of the public المحامي الفقيه export."""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPORT = Path('/home/ubuntu/upload/pasted_file_roJR9N_result.json')
OUT = ROOT / 'almuhame_alfaqih_2026-10-03_screening'
CHANNEL_HANDLE = 'almuhamealfaqih'
SOURCE = 'المحامي الفقيه'
PUBLISHER = 'قناة المحامي الفقيه (@almuhamealfaqih)'

LEGAL = re.compile(
    r'قضاء|قضائ|دعوى|دعاو|محكم|تحكيم|وساط|محام|مرافع|نظام|لائح|قانون|تشريع|تنظيم|'
    r'توثيق|عقد|زواج|طلاق|خلع|حضان|أحوال|تركة|ورث|مواريث|فرائض|وقف|نظار|إثبات|'
    r'بين[ةه]|إقرار|شهاد|تعويض|معاملات|شركة|تجار|مالية|تمويل|عقوب|جناي|جريم|دية|'
    r'ديوان المظالم|صحة|صحي|صياغة|سوابق|قواعد قانونية|موظف عام|حقوق|استراحات|'
    r'المعهد العالي للقضاء|مدونة الأحكام|الاستفادة من السوابق|قائمة بكتبي|'
    r'كيدية|arbitration|settlement|ethics|legal', re.I)
EXCLUDE = re.compile(
    r'رمضان|صيام|زكاة|مناسك|تفسير|سورة|أذكار|دعاء|من يدعوني|مدارج السالكين|'
    r'مختصر كتاب الزكاة|الروض المربع|العقيدة|حديث|كتاب الأدعية|ركض بقلبك|'
    r'الملف الرمضاني|قواعد فقهية كامل|فقه الأسرة|مقرر فقه المعاملات|'
    r'المعيار الشرعي للوقف|عرض مقرر|حاشية على الروض|مكتبة نفع القضائية|'
    r'دبلومات المعهد|الشهادات المهنية|لمحات من العمل|Total events|animation|'
    r'الخرائط الذهنية|كتاب من يدعوني|جدول أصحاب الفروض', re.I)
GENERIC = re.compile(r'^(?:pdf|ttmm|ahwaal|__\d+|المذكرات النسخة النهائية|الوعد|مشكلات أول المعاملات|حماية المسافرين|ملف)', re.I)


def text(message: dict) -> str:
    value = message.get('text', '')
    if isinstance(value, list):
        return ''.join(part.get('text', '') if isinstance(part, dict) else str(part) for part in value)
    return str(value or '')


def title_from_filename(value: str) -> str:
    value = unicodedata.normalize('NFC', value or '')
    value = ''.join(ch for ch in value if unicodedata.category(ch) not in {'Cf', 'So'})
    value = re.sub(r'\.(?:pdf|docx?|mp4)$', '', value, flags=re.I)
    value = value.replace('_', ' ')
    value = re.sub(r'\s+', ' ', value).strip(' -–—.،؛:')
    return value


def norm(value: str) -> str:
    value = unicodedata.normalize('NFC', value or '')
    value = re.sub(r'[\u064B-\u065F\u0670]', '', value)
    value = value.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ٱ', 'ا')
    value = value.replace('ة', 'ه').replace('ى', 'ي')
    value = re.sub(r'\(?\s*نسخة\s+للطباعة\s*\)?', '', value)
    value = re.sub(r'[^\w\u0600-\u06FF]+', '', value.lower())
    return value


def size(bytes_value: object) -> str:
    try: value = int(bytes_value or 0)
    except (ValueError, TypeError): return ''
    if not value: return ''
    return f'{value / 1024 / 1024:.1f} MB' if value >= 1024 * 1024 else f'{value / 1024:.1f} KB'


def category(title: str) -> str:
    if re.search(r'تحكيم|وساط|محكم|arbitration|settlement|ethics', title, re.I): return 'التحكيم والوساطة'
    if re.search(r'محام|مرافع|دعاو', title): return 'المحاماة والمرافعات'
    if re.search(r'أحوال|زواج|طلاق|خلع|حضان|تركة|ورث|مواريث|فرائض', title): return 'الأحوال الشخصية والتركات'
    if re.search(r'قضاء|قضائ|إثبات|بين[ةه]|إقرار|شهاد|سوابق|ديوان المظالم', title): return 'القضاء والإثبات'
    return 'الأنظمة والتشريعات'


def material_type(title: str) -> str:
    if re.search(r'شرح|تبسيط', title): return 'شرح'
    if re.search(r'بحث|دراسة|أوراق|ندوة|تعليق', title): return 'بحث'
    if re.search(r'دليل|فهرس|قائمة|مصطلح', title): return 'دليل'
    if re.search(r'نظام|لائحة|قانون|قواعد|معايير|Code of Ethics|arbitration', title, re.I): return 'نظام'
    return 'كتاب'


def main() -> None:
    OUT.mkdir(exist_ok=True)
    export = json.loads(EXPORT.read_text(encoding='utf-8'))
    current = json.loads((ROOT / 'items.json').read_text(encoding='utf-8'))
    existing = {norm(str(item.get('title') or '')) for item in current if item.get('title')}
    candidates, duplicates, excluded = [], [], []
    seen = set()
    for message in export.get('messages', []):
        filename = message.get('file_name')
        if not filename or str(message.get('mime_type') or '').startswith('video/'):
            continue
        title = title_from_filename(str(filename))
        message_text = text(message)
        # Two exported files have technical names while their public captions identify
        # the legal document precisely; use that explicit caption rather than guessing.
        if message.get('id') == 1119:
            title = 'لائحة عمل أمين سر لجنة التحكيم'
        elif message.get('id') == 1301:
            title = 'الضوابط اللغوية للصياغة القانونية'
        key = norm(title)
        base = {'message_id': message.get('id'), 'title': title, 'file_name': filename, 'mime_type': message.get('mime_type',''), 'file_size': message.get('file_size',0), 'date': message.get('date','')}
        if not key or GENERIC.search(title):
            excluded.append({**base, 'reason':'عنوان تقني أو عام لا يعرّف مادة قانونية بوضوح'})
        elif EXCLUDE.search(title):
            excluded.append({**base, 'reason':'فقه عام أو وعظ أو مادة خارج اختصاص القضاء والأنظمة والمحاماة'})
        elif not LEGAL.search(title + ' ' + message_text):
            excluded.append({**base, 'reason':'لا يحمل العنوان دلالة قانونية أو قضائية كافية'})
        elif key in existing:
            duplicates.append({**base, 'reason':'تطابق عنواني صريح مع مادة قائمة في المكنز'})
        elif key in seen:
            duplicates.append({**base, 'reason':'تطابق عنواني صريح داخل هذا التصدير'})
        else:
            seen.add(key)
            record = {
                'id': f'almuhame_alfaqih_{message["id"]}',
                'title': title,
                'author': '', 'investigator': '', 'publisher': PUBLISHER,
                'year': str(message.get('date',''))[:4] if message.get('date') else '',
                'link_telegram': f'https://t.me/{CHANNEL_HANDLE}/{message["id"]}',
                'link_drive': '', 'link_direct': '',
                'source': SOURCE, 'category': category(title),
                'material_type': material_type(title),
                'file_type': 'Word' if 'wordprocessingml' in str(message.get('mime_type')) else 'PDF',
                'file_size': size(message.get('file_size')),
                'pages_count': '', 'is_featured': False, 'download_links_count': 1,
                'source_message_id': message['id'],
                'integration_note': 'عنوان ورابط رسالة عامة فقط؛ لم يُحمّل الملف.',
            }
            candidates.append(record)
    result = {
        'channel_name': export.get('name'), 'channel_id': export.get('id'), 'channel_handle': CHANNEL_HANDLE,
        'total_messages': len(export.get('messages',[])),
        'file_messages': sum(bool(x.get('file_name')) for x in export.get('messages',[])),
        'new_candidates': len(candidates), 'existing_or_internal_duplicates': len(duplicates), 'excluded': len(excluded),
        'by_category': dict(sorted(Counter(x['category'] for x in candidates).items())),
        'by_material_type': dict(sorted(Counter(x['material_type'] for x in candidates).items())),
        'candidates': candidates, 'duplicates': duplicates, 'excluded_records': excluded,
    }
    (OUT / 'screening_summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (OUT / 'candidates.json').write_text(json.dumps(candidates,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for name, rows in [('candidates.csv',candidates),('duplicates.csv',duplicates),('excluded.csv',excluded)]:
        keys=sorted({k for row in rows for k in row})
        with (OUT / name).open('w',encoding='utf-8-sig',newline='') as fh:
            writer=csv.DictWriter(fh,fieldnames=keys); writer.writeheader(); writer.writerows(rows)
    print(json.dumps({k:result[k] for k in ['channel_name','total_messages','file_messages','new_candidates','existing_or_internal_duplicates','excluded','by_category','by_material_type']},ensure_ascii=False,indent=2))

if __name__ == '__main__': main()
