#!/usr/bin/env python3
"""Build a read-only candidate inventory from public Google Drive listings.

The script does not download any resource files. It only transforms browser-extracted
listing metadata (title, public Drive identifier, and displayed size) into candidate
records for a separate guarded integration step.
"""
from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROOT_LISTING = Path('/home/ubuntu/console_outputs/exec_result_2026-10-01_19-51-54_779.txt')
ROOT_TITLES_LISTING = Path('/home/ubuntu/console_outputs/exec_result_2026-10-01_19-52-30_148.txt')
ANALYSIS_LISTING = Path('/home/ubuntu/console_outputs/exec_result_2026-10-01_19-54-09_296.txt')
DRUG_LISTING = Path('/home/ubuntu/console_outputs/exec_result_2026-10-01_19-59-19_883.txt')
CANDIDATES_PATH = ROOT / 'drive_legal_links_2026-10-01_candidates.json'
AUDIT_PATH = ROOT / 'drive_legal_links_2026-10-01_candidate_audit.json'

ROOT_SOURCE = 'سوابق القضاء العام واللجان'
DRUG_SOURCE = 'DRUG CASES'
GENERAL_SOURCE = 'Google Drive — روابط قانونية'


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def normalize_title(value: str) -> str:
    value = unicodedata.normalize('NFKD', str(value or ''))
    value = ''.join(char for char in value if not unicodedata.combining(char))
    value = value.replace('\u200e', '').replace('\u200f', '').replace('\u2066', '').replace('\u2067', '').replace('\u2068', '').replace('\u2069', '')
    value = value.replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ى', 'ي').replace('ة', 'ه')
    value = re.sub(r'\.(?:pdf|docx?|jpg|jpeg|png)$', '', value, flags=re.I)
    value = re.sub(r'[^\w\d]+', '', value).lower()
    return value


def clean_title(value: str) -> str:
    value = unicodedata.normalize('NFC', str(value or ''))
    value = value.replace('\u200e', '').replace('\u200f', '').replace('\u2066', '').replace('\u2067', '').replace('\u2068', '').replace('\u2069', '')
    value = re.sub(r'\s+(?:PDF|Microsoft Word|Image)$', '', value, flags=re.I)
    value = re.sub(r'\.(?:pdf|docx?|jpg|jpeg|png)$', '', value, flags=re.I)
    value = re.sub(r'\s+', ' ', value).strip(' ._-–—')
    return value


def public_url(file_id: str) -> str:
    return f'https://drive.google.com/file/d/{file_id}/view'


def parse_size(text: str) -> tuple[str, int]:
    match = re.search(r'(\d+(?:[,.]\d+)?)\s*(MB|kB|KB)\b', text or '', flags=re.I)
    if not match:
        return '', 0
    number = float(match.group(1).replace(',', '.'))
    unit = match.group(2).upper()
    if unit == 'KB':
        return f'{number:g} KB', int(number * 1024)
    return f'{number:g} MB', int(number * 1024 * 1024)


def file_type(title: str) -> str:
    suffix = Path(title.strip()).suffix.lower()
    return {
        '.pdf': 'PDF',
        '.doc': 'Word',
        '.docx': 'Word',
        '.jpg': 'JPG',
        '.jpeg': 'JPG',
        '.png': 'PNG',
    }.get(suffix, 'رابط')


def category_for(collection: str, title: str) -> str:
    t = normalize_title(title)
    if collection == 'root':
        if 'اتعابالمحاماه' in t:
            return 'المحاماة والتحكيم'
        if 'افلاس' in t:
            return 'الإفلاس'
        if 'احوالشخصيه' in t:
            return 'الأحوال الشخصية'
        return 'أحكام قضائية'
    if collection == 'analysis':
        return 'أحكام قضائية'
    if collection == 'drug-systems':
        return 'الأنظمة واللوائح'
    if collection == 'drug-rules':
        return 'أحكام قضائية'
    if collection == 'drug-circulars':
        return 'الأنظمة واللوائح'
    if collection == 'drug-precedents':
        return 'أحكام قضائية'
    if collection == 'drug-memos':
        return 'المحاكم والمرافعات'
    if collection == 'lawyer-basics' or collection == 'professional-certificates':
        return 'المحاماة والتحكيم'
    if collection == 'company-policies':
        return 'الأنظمة واللوائح'
    if collection == 'legal-memos':
        return 'المحاكم والمرافعات'
    return 'أحكام قضائية'


def material_type_for(collection: str, title: str) -> str:
    t = normalize_title(title)
    if collection == 'root':
        return 'فهرس' if 'فهرس' in t else 'أحكام'
    if collection == 'analysis':
        return 'دليل'
    if collection == 'drug-systems':
        return 'نظام'
    if collection == 'drug-rules':
        if 'دليل' in t:
            return 'دليل'
        if 'بحث' in t:
            return 'بحث'
        return 'أحكام'
    if collection == 'drug-circulars':
        return 'تعميم'
    if collection == 'drug-precedents':
        return 'حكم قضائي'
    if collection == 'drug-memos' or collection == 'legal-memos':
        return 'مذكرة'
    if collection == 'precedents-merged':
        return 'أحكام'
    if collection == 'company-policies':
        return 'دليل'
    if collection == 'professional-certificates' or collection == 'lawyer-basics':
        return 'دليل'
    if collection == 'fiqh-courts':
        return 'كتاب'
    return 'عنوان مرجعي'


def source_for(collection: str) -> str:
    if collection.startswith('drug-'):
        return DRUG_SOURCE
    if collection in {'root', 'analysis'}:
        return ROOT_SOURCE
    return GENERAL_SOURCE


def candidate(file_id: str, raw_title: str, raw_text: str, collection: str) -> dict:
    title = clean_title(raw_title)
    size, size_bytes = parse_size(raw_text)
    return {
        'id': f'drive_{collection.replace("-", "_")}_{file_id}',
        'title': title,
        'author': '',
        'investigator': '',
        'publisher': source_for(collection),
        'year': '',
        'link_telegram': '',
        'link_drive': public_url(file_id),
        'link_direct': '',
        'source': source_for(collection),
        'category': category_for(collection, title),
        'material_type': material_type_for(collection, title),
        'file_type': file_type(raw_title),
        'file_size': size,
        'pages_count': '',
        'is_featured': False,
        'download_links_count': 1,
        '_collection': collection,
        '_drive_file_id': file_id,
        '_size_bytes': size_bytes,
    }


def main() -> None:
    root_rows = load_json(ROOT_LISTING)
    root_title_rows = load_json(ROOT_TITLES_LISTING)
    analysis_rows = load_json(ANALYSIS_LISTING)
    drug_groups = load_json(DRUG_LISTING)
    root_titles = {row['id']: row.get('title', '') for row in root_title_rows}

    proposed: list[dict] = []
    excluded: list[dict] = []

    # Main public folder: retain documents; subfolders are evaluated separately below.
    for row in root_rows:
        title = root_titles.get(row['id'], '')
        if 'Carpeta' in title:
            excluded.append({'id': row['id'], 'title': clean_title(title), 'reason': 'مجلد فرعي؛ فُهرست محتوياته عند صلتها القضائية'})
            continue
        proposed.append(candidate(row['id'], title, row.get('text', ''), 'root'))

    # Relevant precedent-analysis subfolder.
    for row in analysis_rows:
        proposed.append(candidate(row['id'], row.get('title', ''), row.get('text', ''), 'analysis'))

    drug_collection = {
        'أنظمة': 'drug-systems',
        'تسبيبات و قواعد': 'drug-rules',
        'تعاميم': 'drug-circulars',
        'سوابق': 'drug-precedents',
        'مذكرات': 'drug-memos',
    }
    for group in drug_groups:
        collection = drug_collection[group['folder']]
        for row in group['rows']:
            proposed.append(candidate(row['id'], row.get('title', ''), row.get('text', ''), collection))

    # Individually supplied, publicly accessible Drive files.
    singles = [
        ('1Wj3V5LNQvhxqZjYkDJ3Z3PcZmgvgK5W6', 'القواعد الفقهية وتطبيقاتها في المحاكم.pdf', '', 'fiqh-courts'),
        ('1GDZWk13TEV_EyOHTuZvxgMGdrAnYSbVe', 'أهم الأساسيات بمهنة المحاماة.pdf', '', 'lawyer-basics'),
        ('15JvoRQpfqxQPMYIayqjlOtBVUj3-kWou', 'دليل أهم الشهادات المهنية في المجال القانوني — حصة المبرد.pdf', '', 'professional-certificates'),
        ('1WWSwpIyNE8Ae2pcNu8PBoJzSAItGuhmj', 'أهم اللوائح والسياسات اللازمة لعمل الشركات ونبذة عنها.pdf', '', 'company-policies'),
        ('1k4A4GSuZd3b_enunOlFb2x0lngbXx5fp', 'تجميعات نماذج من المذكرات القانونية — سبل القانون.pdf', '', 'legal-memos'),
        ('1xhJPX18d1gfX9rWuyMmDWah0bctpEPYy', 'سوابق قضائية مدمجة.pdf', '', 'precedents-merged'),
    ]
    for entry in singles:
        proposed.append(candidate(*entry))

    # Retain one distinct item per normalised candidate title. Where two public links
    # have the same title, retain the larger display-size variant; ties retain first.
    retained_by_title: dict[str, dict] = {}
    internal_duplicates: list[dict] = []
    for row in proposed:
        key = normalize_title(row['title'])
        if not key:
            excluded.append({'id': row['_drive_file_id'], 'title': row['title'], 'reason': 'عنوان فارغ بعد تنظيف اسم الملف'})
            continue
        previous = retained_by_title.get(key)
        if previous is None:
            retained_by_title[key] = row
            continue
        keep, drop = (row, previous) if row['_size_bytes'] > previous['_size_bytes'] else (previous, row)
        retained_by_title[key] = keep
        internal_duplicates.append({
            'kept_drive_file_id': keep['_drive_file_id'],
            'kept_title': keep['title'],
            'kept_url': keep['link_drive'],
            'removed_drive_file_id': drop['_drive_file_id'],
            'removed_title': drop['title'],
            'removed_url': drop['link_drive'],
            'reason': 'تطابق العنوان بعد التطبيع داخل الدفعة؛ احتُفظ بالرابط ذي الحجم المعروض الأكبر، أو الأول عند تساوي الحجم',
        })

    candidates = list(retained_by_title.values())
    candidates.sort(key=lambda row: (row['_collection'], row['title']))
    for row in candidates:
        row.pop('_size_bytes', None)

    audit = {
        'source_listing': {
            'root_folder': 'https://drive.google.com/drive/folders/10aCRPcVE068hJY6-Y6eORb82byMomjqu',
            'drug_cases_folder': 'https://drive.google.com/drive/folders/10GJ5gSwndof7QVd3b1A-A18uCTZp5Fcb',
            'extraction_method': 'صفحات العرض العامة في Google Drive فقط؛ لم تُنزّل الملفات.',
        },
        'raw_root_rows': len(root_rows),
        'raw_analysis_rows': len(analysis_rows),
        'raw_drug_rows': sum(len(group['rows']) for group in drug_groups),
        'raw_individual_rows': len(singles),
        'proposed_before_internal_deduplication': len(proposed),
        'retained_candidates': len(candidates),
        'excluded_non_material_or_folder_rows': excluded,
        'internal_duplicate_candidates': internal_duplicates,
        'candidates': candidates,
    }
    CANDIDATES_PATH.write_text(json.dumps(candidates, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    AUDIT_PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'raw_root_rows': len(root_rows),
        'raw_analysis_rows': len(analysis_rows),
        'raw_drug_rows': sum(len(group['rows']) for group in drug_groups),
        'raw_individual_rows': len(singles),
        'candidate_count': len(candidates),
        'internal_duplicates_removed': len(internal_duplicates),
        'excluded': len(excluded),
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
