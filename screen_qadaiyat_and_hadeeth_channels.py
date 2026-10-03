#!/usr/bin/env python3
"""Create a conservative, read-only candidate manifest from two Telegram exports.

The script never changes the catalogue.  It keeps only document records whose cleaned
file titles make their legal or judicial relevance clear, then eliminates existing and
in-batch duplicate titles by normalized title.
"""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'qadaiyat_and_hadeeth_2026-10-03_screening'
OUT.mkdir(exist_ok=True)
CATALOGUE = ROOT / 'items.json'
CHANNELS = [
    {
        'key': 'qadaiyat',
        'source': 'قضائيات',
        'publisher': 'قضائيات',
        'path': Path('/home/ubuntu/upload/pasted_file_uqMGlj_result.json'),
        'url_template': 'https://t.me/abdullatif100/{message_id}',
    },
    {
        'key': 'hadeeth_law',
        'source': 'حديث القانون — المنصة القانونية للمحامين',
        'publisher': 'حديث القانون — المنصة القانونية للمحامين',
        'path': Path('/home/ubuntu/upload/pasted_file_RrXmgW_result.json'),
        # The exported public channel has no verified handle in its JSON.  This is
        # the deterministic Telegram message path derived from its exported channel ID.
        'url_template': 'https://t.me/c/2258360695/{message_id}',
    },
    {
        'key': 'rabab_library',
        'source': 'مكتبة المحامية رباب المعبي',
        'publisher': 'مكتبة المحامية رباب المعبي',
        'path': Path('/home/ubuntu/upload/pasted_file_di1Hxm_result.json'),
        # The export identifies this as a public channel, but does not provide a
        # public handle. Retain its Telegram message route from the export ID.
        'url_template': 'https://t.me/c/1352319266/{message_id}',
    },
    {
        'key': 'wejdan_zahrani',
        'source': 'المحامية وجدان الزهراني ⚖️',
        'publisher': 'المحامية وجدان الزهراني ⚖️',
        'path': Path('/home/ubuntu/upload/pasted_file_6UlS0Z_result.json'),
        # The export has no public handle; retain the deterministic message route
        # built from the exported Telegram channel ID.
        'url_template': 'https://t.me/c/1777689267/{message_id}',
    },
]

DOCUMENT_MIMES = {
    'application/pdf': 'PDF',
    'application/msword': 'Word',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word',
    'application/vnd.ms-excel': 'Excel',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PPTX',
}

# A title must contain one of these after cleaning.  Terms such as "حكم" or "فقه"
# are intentionally omitted because they are too broad outside a legal context.
# Long roots are specific enough to match inside normalized words.  Short/common
# Arabic words are handled separately as whole tokens so, for example, "اعمل أقل"
# is not mistaken for an employment-law title.
SCOPE_ROOTS = [
    'قضائ', 'قاضي', 'قضاة', 'محكم', 'محام', 'دعوى', 'دعاو', 'قانون', 'نظام', 'لائح',
    'تشريع', 'دستور', 'مرافع', 'اجراء', 'استئناف', 'نقض', 'التماس', 'تنفيذ', 'اثبات',
    'تحكيم', 'وساط', 'جزاء', 'جنائ', 'جريم', 'عقوب', 'ادعاء', 'نياب', 'اختصاص',
    'تعويض', 'مسؤول', 'التزام', 'شرك', 'تجار', 'افلاس', 'اعسار', 'ضريب', 'جمارك',
    'ملكيهفكريه', 'علاماتتجاريه', 'عمال', 'اجير', 'احوالشخصيه', 'تركات', 'مواريث',
    'مصرف', 'بنك', 'تامين', 'استثمار', 'عقار', 'عقاري', 'اداري', 'مخدر', 'تزوير',
    'فساد', 'رشوة', 'اتصالات', 'بيئه', 'قانوندولي', 'منظماتدوليه', 'سلطةقضائيه',
    'صيغقانونيه', 'منهجيةقانونيه', 'مستهلك', 'منافس', 'تخصيص', 'تمويل',
]
SCOPE_WORDS = {
    'عقد', 'عقود', 'وقف', 'وصية', 'وصايا', 'إرث', 'ارث', 'محكمة', 'محاكم', 'أحكام',
    'احكام', 'حكم', 'قضاة', 'قاضي', 'شهادة', 'دليل', 'قانونية', 'قضائية', 'دعاوى',
    'دعوى', 'لائحة', 'قرار', 'تعميم', 'مرافعات', 'إثبات', 'اثبات', 'تنفيذ', 'محاماة',
    'وساطة', 'تحكيم', 'جناية', 'جنائي', 'جزائي', 'تعويض', 'ضمان', 'التزام',
}

# Explicit non-legal contexts from the exports; these are applied only when no scope
# term remains after cleaning. They prevent broad faith/education material from entry.
NONLEGAL_PATTERNS = [
    r'مقاصد الشريعه', r'احكام التجويد', r'علوم القران', r'تفسير', r'سيره', r'عقيده',
    r'الحديث النبوي', r'الاعجاز', r'الدعوة', r'فقه العبادات', r'الرقية', r'الخطب',
    r'الاخلاق', r'الادب العربي', r'تعليم', r'مدرس', r'جامعه',
]

NOISE_PREFIX = re.compile(r'^(?:figh|women|econom|archivetemp|emailing|e0xez|noor-book\.com)[\s_\-\d]+', re.I)
NOISE_SUFFIX = re.compile(r'(?:\s+(?:موقع\s*النقض|مكتبة\s*عبدالله|نسخة\s*معدلة|نسخة\s*علي\s*الفايز|pdf|secured))+$', re.I)
EXT = re.compile(r'\.(?:pdf|docx?|xlsx?|pptx?|zip|rar|mp3|m4a|ogg|mp4|jpg|jpeg|png)$', re.I)


def flatten(value) -> str:
    if value is None:
        return ''
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return ''.join(flatten(v) for v in value)
    if isinstance(value, dict):
        return str(value.get('text', ''))
    return str(value)


def clean_title(value: str) -> str:
    value = value or ''
    # Files sometimes contain repeated .pdf markers after the true extension.
    while True:
        newer = EXT.sub('', value).strip()
        if newer == value:
            break
        value = newer
    value = value.replace('_', ' ').replace('\u00a0', ' ').replace('ـ', ' ')
    value = NOISE_PREFIX.sub('', value).strip()
    value = re.sub(r'\b(?:pdf|docx?|xlsx?|pptx?)\b', ' ', value, flags=re.I)
    value = re.sub(r'\s+', ' ', value).strip(' ._-–—')
    value = NOISE_SUFFIX.sub('', value).strip(' ._-–—')
    return value


def norm(value: str) -> str:
    value = unicodedata.normalize('NFKD', value or '')
    value = ''.join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower().translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'))
    value = value.replace('أ','ا').replace('إ','ا').replace('آ','ا').replace('ٱ','ا').replace('ى','ي').replace('ة','ه')
    return re.sub(r'[^\w\u0600-\u06ff]+', '', value)


def readable_norm(value: str) -> str:
    value = unicodedata.normalize('NFKD', value or '')
    value = ''.join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower().replace('أ','ا').replace('إ','ا').replace('آ','ا').replace('ٱ','ا').replace('ى','ي').replace('ة','ه')
    return re.sub(r'[^\w\u0600-\u06ff]+', ' ', value).strip()


def scope_reason(title: str) -> str | None:
    packed = norm(title)
    human = readable_norm(title)
    if any(re.search(pattern, human) for pattern in NONLEGAL_PATTERNS):
        return None
    words = set(human.split())
    terms = [term for term in SCOPE_ROOTS if term in packed]
    terms += [term for term in SCOPE_WORDS if term in words]
    if terms:
        return 'عنوان قانوني/قضائي واضح: ' + '، '.join(dict.fromkeys(terms[:4]))
    return None


def category(title: str) -> str:
    t = norm(title)
    if any(x in t for x in ('محام','مهنةالمحام','حصانةالمحام')): return 'المحاماة والتمثيل القانوني'
    if any(x in t for x in ('تحكيم','وساط')): return 'التحكيم والوساطة'
    if any(x in t for x in ('جنائ','جريم','عقوب','مخدر','تزوير','رشوة','فساد')): return 'القانون الجنائي'
    if any(x in t for x in ('تجار','شرك','افلاس','اعسار','بنك','مصرف','تجار','استثمار')): return 'القانون التجاري'
    if any(x in t for x in ('عقد','التزام','مسؤول','تعويض','مدني','عقار','عقاري')): return 'القانون المدني'
    if any(x in t for x in ('اداري','سلطةقضائيه','مجلسالدوله')): return 'القضاء الإداري'
    if any(x in t for x in ('احوالشخصيه','تركات','مواريث','ارث','وصيه','وقف')): return 'الأحوال الشخصية'
    if any(x in t for x in ('عمال','قانونالعمل','اجير')): return 'القانون العمالي'
    if any(x in t for x in ('دستور','سلطات','دستوري')): return 'القانون الدستوري'
    if any(x in t for x in ('مرافع','دعوى','اجراء','استئناف','نقض','التماس','اثبات','تنفيذ','اختصاص','قضائ','محكم')): return 'المحاكم والمرافعات'
    return 'الأبحاث القانونية والقضائية'


def material_type(title: str) -> str:
    t = norm(title)
    if any(x in t for x in ('قانون','نظام','لائح','تشريع','قراروزير','تعميم')): return 'نظام'
    if any(x in t for x in ('حكم','احكام','قضاءالنقض','مبادئ')): return 'أحكام'
    if 'مجله' in t: return 'مجلة'
    if any(x in t for x in ('بحث','دراسه','رساله')): return 'بحث'
    if any(x in t for x in ('دليل','خارطه','نموذج')): return 'دليل'
    return 'كتاب'


def file_size(value) -> str:
    try:
        n = int(value)
    except (ValueError, TypeError):
        return ''
    if n >= 1024 * 1024:
        return f'{n / (1024 * 1024):.1f} MB'
    return f'{n / 1024:.0f} KB'


def generic_filename_title(title: str) -> bool:
    """Return True for names such as 36.pdf or random file-code strings."""
    packed = norm(title)
    return (
        not packed or packed.isdigit() or len(packed) < 6 or
        bool(re.fullmatch(r'(?:allj|[a-z]+)?\d+[a-z\d]*', packed))
    )


def caption_title(value) -> str:
    """Extract the visible resource title from a numbered channel post."""
    value = re.sub(r'^\s*\d+\s*[_|\-–—.]?\s*', '', value or '')
    value = re.sub(r'\s+', ' ', value).strip(' ._-–—')
    return clean_title(value)


def main() -> None:
    current = json.loads(CATALOGUE.read_text(encoding='utf-8'))
    current_ids = {str(x.get('id')) for x in current}
    current_by_norm: dict[str, list[dict]] = {}
    for item in current:
        key = norm(clean_title(str(item.get('title',''))))
        if key:
            current_by_norm.setdefault(key, []).append(item)

    all_rows: list[dict] = []
    source_summary = []
    for channel in CHANNELS:
        data = json.loads(channel['path'].read_text(encoding='utf-8'))
        stats = Counter()
        last_text = ''
        last_text_date = ''
        for message in data.get('messages', []):
            stats['all_messages'] += 1
            mime = str(message.get('mime_type') or '')
            file_name = str(message.get('file_name') or '')
            if not file_name:
                text = flatten(message.get('text')).strip()
                if text:
                    last_text = text
                    last_text_date = str(message.get('date') or '')
                continue
            stats['file_messages'] += 1
            title = clean_title(file_name)
            # In the Rabab export a descriptive text post is occasionally sent a
            # few seconds before a generically named document. Reuse it only when
            # it is demonstrably adjacent in time; otherwise skip ambiguous files.
            if generic_filename_title(title) and last_text and last_text_date:
                try:
                    before = datetime.fromisoformat(last_text_date)
                    current_date = datetime.fromisoformat(str(message.get('date') or ''))
                    seconds = (current_date - before).total_seconds()
                except ValueError:
                    seconds = 999999
                candidate = caption_title(last_text)
                if 0 <= seconds <= 180 and candidate:
                    title = candidate
            if not title:
                stats['bad_title'] += 1
                continue
            if mime not in DOCUMENT_MIMES:
                stats['non_document_file'] += 1
                continue
            stats['document_files'] += 1
            message_id = int(message.get('id'))
            norm_title = norm(title)
            existing = current_by_norm.get(norm_title, [])
            reason = scope_reason(title)
            row = {
                'channel_key': channel['key'],
                'channel_name': channel['source'],
                'channel_export_id': str(data.get('id')),
                'message_id': str(message_id),
                'suggested_id': f"{channel['key']}_{message_id}",
                'title': title,
                'normalized_title': norm_title,
                'mime_type': mime,
                'file_type': DOCUMENT_MIMES[mime],
                'file_size': file_size(message.get('file_size')),
                'date': str(message.get('date') or ''),
                'official_url': channel['url_template'].format(message_id=message_id),
                'existing_exact_ids': ' | '.join(str(x.get('id')) for x in existing),
                'existing_exact_titles': ' | '.join(str(x.get('title')) for x in existing),
                'scope_reason': reason or '',
                'status': '',
                'status_reason': '',
                'category': category(title),
                'material_type': material_type(title),
            }
            if existing:
                row['status'] = 'EXCLUDE_EXISTING_EXACT_DUPLICATE'
                row['status_reason'] = 'عنوان مطابق بعد التطبيع موجود بالفعل في المكنز.'
                stats['existing_exact_duplicate'] += 1
            elif not reason:
                row['status'] = 'EXCLUDE_NOT_CLEARLY_IN_SCOPE'
                row['status_reason'] = 'العنوان لا يثبت اتصالاً قانونياً أو قضائياً واضحاً وفق معيار الإدخال المتحفظ.'
                stats['not_clear_scope'] += 1
            else:
                row['status'] = 'PENDING_IN_BATCH_DEDUPLICATION'
                row['status_reason'] = reason
                stats['initial_keep'] += 1
            all_rows.append(row)
        source_summary.append({
            'channel_key': channel['key'], 'channel_name': channel['source'],
            'channel_export_id': data.get('id'), **stats
        })

    # If the two exports share an exact title (or a channel repeats it), retain the first
    # chronological message and exclude all later identical normalized titles.
    by_norm: dict[str, list[dict]] = {}
    for row in all_rows:
        if row['status'] == 'PENDING_IN_BATCH_DEDUPLICATION':
            by_norm.setdefault(row['normalized_title'], []).append(row)
    for rows in by_norm.values():
        rows.sort(key=lambda r: (r['date'], r['channel_key'], int(r['message_id'])))
        winner = rows[0]
        winner['status'] = 'KEEP'
        winner['status_reason'] = winner['scope_reason'] + '؛ لا يظهر له تطابق عنواني تام في المكنز أو داخل الدفعة.'
        for loser in rows[1:]:
            loser['status'] = 'EXCLUDE_IN_BATCH_EXACT_DUPLICATE'
            loser['status_reason'] = f"عنوان مطابق بعد التطبيع ضمن الدفعة؛ أُبقي {winner['suggested_id']} فقط."

    if any(row['suggested_id'] in current_ids for row in all_rows):
        raise SystemExit('Suggested ID collision with existing catalogue')

    keep = [row for row in all_rows if row['status'] == 'KEEP']
    fieldnames = list(all_rows[0])
    for name, rows in [('all_screened_records.csv', all_rows), ('keep_candidates.csv', keep)]:
        with (OUT / name).open('w', encoding='utf-8-sig', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader(); writer.writerows(rows)

    manifest = []
    for row in keep:
        year = row['date'][:4] if re.fullmatch(r'\d{4}', row['date'][:4]) else ''
        manifest.append({
            'id': row['suggested_id'], 'title': row['title'], 'author': '', 'investigator': '',
            'publisher': row['channel_name'], 'year': year, 'link_telegram': row['official_url'],
            'link_drive': '', 'link_direct': '', 'source': row['channel_name'],
            'category': row['category'], 'material_type': row['material_type'], 'file_type': row['file_type'],
            'file_size': row['file_size'], 'pages_count': '', 'is_featured': False, 'download_links_count': 1,
            'integration_note': 'سجل إحالي مستخرج من تصدير القناة؛ لم يُحمّل الملف.',
        })
    (OUT / 'keep_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    result = {
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'catalogue_total_before': len(current),
        'sources': source_summary,
        'all_document_records_screened': sum(1 for x in all_rows if x['mime_type'] in DOCUMENT_MIMES),
        'status_counts': dict(sorted(Counter(x['status'] for x in all_rows).items())),
        'keep_count': len(keep),
        'keep_by_source': dict(sorted(Counter(x['channel_name'] for x in keep).items())),
        'keep_by_category': dict(sorted(Counter(x['category'] for x in keep).items())),
        'keep_by_material_type': dict(sorted(Counter(x['material_type'] for x in keep).items())),
        'notes': [
            'لم تُعدّل بيانات المكنز في هذه المرحلة.',
            'المقارنة هنا عنوانية تامة بعد تنظيف أسماء الملفات فقط؛ لم يُنفذ دمج أو حذف للسجلات القائمة.',
            'لا تُضاف ملفات الوسائط والصور والأرشيفات أو العناوين غير القانونية الواضحة.',
            'مصدر «حديث القانون» لا يتضمن في ملف التصدير معرفاً عاماً مثبتاً؛ لذلك حُفظ رابط رسالة تيليجرام بالمعرف العددي المستخرج من ملف القناة فقط.',
        ],
    }
    (OUT / 'screening_summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
