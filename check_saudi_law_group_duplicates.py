import json
import re
from difflib import SequenceMatcher
from pathlib import Path

ITEMS = Path('/home/ubuntu/makanez-qadaa/items.json')
CANDIDATES = Path('/home/ubuntu/makanez-qadaa/saudi_law_group_file_candidates.json')
OUTPUT = Path('/home/ubuntu/makanez-qadaa/saudi_law_group_ready.json')

# وثائق ذات عنوان واضح أو جهة صادرة محددة؛ تستبعد المسودات والأسئلة والاستشارات الفردية.
APPROVED_IDS = {112299, 112300, 112301, 112902, 112908, 118665, 138003, 140225, 147878}

def norm(value):
    value = value or ''
    value = value.lower().replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ى', 'ي').replace('ة', 'ه')
    value = re.sub(r'[\W_]+', '', value, flags=re.UNICODE)
    return value

def category_for(title):
    if 'تجاري' in title:
        return 'القانون التجاري'
    if 'عمل' in title:
        return 'الأنظمة والتشريعات'
    if 'ديوان المظالم' in title or 'هيئة التدقيق' in title:
        return 'القضاء الإداري'
    return 'القضاء والمحاكم'

def type_for(title):
    if 'قرار' in title:
        return 'قرار'
    if 'دليل' in title:
        return 'دليل'
    if 'جدول' in title:
        return 'لائحة'
    return 'أحكام'

def main():
    items = json.loads(ITEMS.read_text(encoding='utf-8'))
    candidates = json.loads(CANDIDATES.read_text(encoding='utf-8')).get('selected', [])
    existing = [(item.get('id'), item.get('title', ''), norm(item.get('title', ''))) for item in items]
    accepted, duplicates, excluded = [], [], []
    for candidate in candidates:
        if candidate['id'] not in APPROVED_IDS:
            excluded.append({'id': candidate['id'], 'title': candidate['title'], 'reason': 'عنوان غير موثق كوثيقة رسمية أو يمثل مسودة/مادة متقادمة أو استشارة'})
            continue
        title_norm = norm(candidate['title'])
        match = None
        for existing_id, existing_title, existing_norm in existing:
            ratio = SequenceMatcher(None, title_norm, existing_norm).ratio()
            if title_norm == existing_norm or (min(len(title_norm), len(existing_norm)) > 20 and (title_norm in existing_norm or existing_norm in title_norm)) or ratio >= 0.93:
                match = {'id': existing_id, 'title': existing_title, 'similarity': round(ratio, 3)}
                break
        if match:
            duplicates.append({'id': candidate['id'], 'title': candidate['title'], 'existing': match})
            continue
        title = re.sub(r'\s*\.pdf\s*$', '', candidate['title'], flags=re.I).strip()
        accepted.append({
            'id': f"saudi_law_group_{candidate['id']}",
            'title': title,
            'author': '',
            'investigator': '',
            'link_telegram': candidate['telegram_link'],
            'link_drive': '',
            'link_direct': '',
            'source': 'قناة المحاماة والقانون السعودي',
            'category': category_for(title),
            'material_type': type_for(title),
            'file_type': 'PDF',
            'file_size': '',
            'pages_count': '',
            'is_featured': False,
            'download_links_count': 1,
        })
    OUTPUT.write_text(json.dumps({'accepted': accepted, 'duplicates': duplicates, 'excluded': excluded}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'accepted': len(accepted), 'duplicates': len(duplicates), 'excluded': len(excluded)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
