#!/usr/bin/env python3
"""Build a read-only, deterministic candidate inventory from Tabseet article anchors."""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
SITE_AUDIT = Path('/home/ubuntu/tabseet-site-audit-2026-10-02')
HTML_FILE = SITE_AUDIT / 'tabseet.html'
OUT_JSON = ROOT / 'tabseet_civil_articles_2026-10-02_candidates.json'
OUT_CSV = ROOT / 'tabseet_civil_articles_2026-10-02_candidates.csv'
BASE_URL = 'https://saudalbazei.com/tabseet/'


def normalize(value: str) -> str:
    value = unicodedata.normalize('NFKD', value or '')
    value = ''.join(ch for ch in value if not unicodedata.combining(ch))
    value = (value.lower().replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
             .replace('ى', 'ي').replace('ة', 'ه'))
    return re.sub(r'[^\w\u0600-\u06ff]+', '', value)


ARABIC_INDIC_DIGITS = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')


def canonical_title(source_title: str) -> tuple[str, str]:
    """Produce a searchable, compact article title while retaining the source title."""
    match = re.search(r'،\s*المادة\s+([٠-٩]+)\s+(.+)$', source_title)
    if not match:
        raise RuntimeError(f'Unexpected Tabseet article heading: {source_title!r}')
    article_number = match.group(1).translate(ARABIC_INDIC_DIGITS)
    topic = match.group(2).strip()
    return f'نظام المعاملات المدنية: المادة {article_number} — {topic}', source_title


def main() -> None:
    html = HTML_FILE.read_text(encoding='utf-8', errors='replace')
    soup = BeautifulSoup(html, 'html.parser')
    existing = json.loads((ROOT / 'items.json').read_text(encoding='utf-8'))
    existing_ids = {str(x.get('id', '')) for x in existing}
    existing_titles = {normalize(str(x.get('title', ''))) for x in existing}
    existing_links = {
        str(x.get(field, '') or '')
        for x in existing
        for field in ('link_direct', 'link_drive', 'link_telegram')
    }

    rows = []
    for article in soup.find_all('article', id=re.compile(r'^a\d+$')):
        number = int(article['id'][1:])
        heading = article.find(['h1', 'h2', 'h3', 'h4'])
        if heading is None:
            raise RuntimeError(f'Missing heading for {article["id"]}')
        title, source_title = canonical_title(heading.get_text(' ', strip=True))
        breadcrumb = ''
        companion = soup.find(id=f'b{number}')
        if companion:
            first_div = companion.find(class_='crumb') or companion.find('div')
            if first_div:
                breadcrumb = first_div.get_text(' ', strip=True)
        record = {
            'id': f'tabseet_ncm_{number:03d}',
            'title': title,
            'author': 'منصة تبسيط',
            'investigator': '',
            'publisher': 'منصة تبسيط',
            'year': '',
            'link_telegram': '',
            'link_drive': '',
            'link_direct': f'{BASE_URL}#a{number}',
            'source': 'منصة تبسيط',
            'category': 'الأنظمة والتشريعات',
            'material_type': 'شرح',
            'file_type': 'رابط',
            'file_size': '',
            'pages_count': '',
            'is_featured': False,
            'download_links_count': 1,
            'source_anchor': article['id'],
            'source_title': source_title,
            'source_breadcrumb': breadcrumb,
        }
        if record['id'] in existing_ids:
            raise RuntimeError(f'Existing ID collision: {record["id"]}')
        if record['link_direct'] in existing_links:
            raise RuntimeError(f'Existing direct link collision: {record["link_direct"]}')
        if normalize(record['title']) in existing_titles:
            raise RuntimeError(f'Existing normalized title collision: {record["title"]}')
        rows.append(record)

    if len(rows) != 721:
        raise RuntimeError(f'Expected exactly 721 article anchors; found {len(rows)}')
    ids = [x['id'] for x in rows]
    titles = [normalize(x['title']) for x in rows]
    links = [x['link_direct'] for x in rows]
    if len(ids) != len(set(ids)) or len(titles) != len(set(titles)) or len(links) != len(set(links)):
        raise RuntimeError('Candidate IDs, normalized titles, or links are not unique')

    OUT_JSON.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    with OUT_CSV.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print(json.dumps({
        'candidate_count': len(rows),
        'first': rows[0],
        'last': rows[-1],
        'categories': Counter(x['category'] for x in rows),
        'material_types': Counter(x['material_type'] for x in rows),
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
