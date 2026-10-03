#!/usr/bin/env python3
"""Build a reviewable candidate list from verified KSU law journal TOCs only."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path('/home/ubuntu/makanez-qadaa')
SOURCE = Path('/home/ubuntu/ksu-law-journal-archive-2026-10-03/extracted_article_titles.json')
OUT = ROOT / 'ksu_law_journal_recent_2026-10-03_candidates.json'

GREGORIAN_YEAR = {25: '2022', 27: '2023', 28: '2023', 29: '2024', 30: '2024', 31: '2025', 32: '2026'}


def issue_codes(label: str) -> tuple[str, str]:
    nums = re.findall(r'\d+', label)
    if len(nums) < 2:
        raise ValueError(f'Cannot parse volume/issue: {label}')
    return nums[0], nums[1]


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding='utf-8'))
    rows = []
    for issue in source['issues']:
        volume, number = issue_codes(issue['issue_label'])
        for article_index, article in enumerate(issue['articles'], 1):
            rows.append({
                'id': f'ksu_lps_v{volume}_i{number}_{article_index:02d}',
                'title': article['title'],
                'author': article['author'],
                'investigator': '',
                'publisher': 'جامعة الملك سعود',
                'year': GREGORIAN_YEAR[issue['archive_index']],
                'link_telegram': '',
                'link_drive': '',
                'link_direct': issue['official_issue_url'],
                'source': 'مجلة جامعة الملك سعود للحقوق والعلوم السياسية',
                'category': 'البحوث القانونية والسياسية',
                'material_type': 'بحث',
                'file_type': 'PDF',
                'file_size': '',
                'pages_count': '',
                'is_featured': False,
                'download_links_count': 1,
                'issue_label': issue['issue_label'],
                'issue_archive_index': issue['archive_index'],
                'start_page': article['start_page'],
                'source_archive_url': source['source_archive_url'],
            })
    assert len(rows) == source['article_count_raw'] == 56
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'candidate_count': len(rows), 'output': str(OUT)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
