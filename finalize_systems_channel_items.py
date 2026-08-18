import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path('/home/ubuntu/makanez-qadaa')
INPUT = ROOT / 'systems_channel_ready.json'
OUTPUT = ROOT / 'systems_channel_final.json'

INCOMPLETE = re.compile(r'(الخبراء|الجديد\s*٢٠٢٣|في المملكة العربية السعودية|مهنة المحاسبة و$|التجارة.*الامتياز|مراقبة شركات التأمين$|مهنة المحاسبة والمراجعة وتنظيم)', re.I)

def key(value):
    value = unicodedata.normalize('NFKD', value or '')
    value = ''.join(char for char in value if not unicodedata.combining(char))
    value = value.lower().replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').replace('ى', 'ي').replace('ة', 'ه')
    value = re.sub(r'(الجديد|في المملكه العربيه السعوديه|٢٠\d\d|\d+|:)', ' ', value)
    value = re.sub(r'[^\w\u0600-\u06ff]+', '', value)
    return value

def main():
    source = json.loads(INPUT.read_text(encoding='utf-8'))
    accepted, removed = [], []
    for item in source['ready']:
        title = item['title']
        title = title.replace('المهني2ة', 'المهنية').replace('المنافس2ة', 'المنافسة').replace('الأموال2', 'الأموال')
        item['title'] = title
        if INCOMPLETE.search(title):
            removed.append({'id': item['id'], 'title': title, 'reason': 'عنوان دراسي أو غير مستقل'})
            continue
        candidate_key = key(title)
        duplicate = None
        for kept in accepted:
            kept_key = key(kept['title'])
            ratio = SequenceMatcher(None, candidate_key, kept_key).ratio()
            if candidate_key == kept_key or ratio >= 0.91:
                duplicate = kept
                break
        if duplicate:
            removed.append({'id': item['id'], 'title': title, 'reason': 'نسخة مكررة أو صياغة بديلة', 'kept_id': duplicate['id'], 'kept_title': duplicate['title']})
            continue
        accepted.append(item)
    result = {
        'source_name': source['source_name'],
        'ready_count': len(accepted),
        'excluded_internal_duplicates': len(removed),
        'ready': accepted,
        'removed': removed,
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'ready_count': len(accepted), 'excluded_internal_duplicates': len(removed)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
