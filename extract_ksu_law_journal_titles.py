#!/usr/bin/env python3
"""Fast, reviewable extraction of article titles from official KSU law journal PDFs.

Reads only likely table-of-contents pages (6–8); if absent, retries pages 4–5.
It sends page images to a vision model using strict JSON output, preserving only
visible information and writing a source artifact outside the web dataset.
"""
from __future__ import annotations

import base64
import concurrent.futures
import json
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

WORKDIR = Path('/home/ubuntu/ksu-law-journal-archive-2026-10-03')
MANIFEST = WORKDIR / 'archive_manifest.json'
ISSUES_DIR = WORKDIR / 'issues'
RENDER_DIR = WORKDIR / 'quick-toc-images'
OUT = WORKDIR / 'extracted_article_titles.json'
MODEL = 'gpt-5-mini'
WORKERS = 4
# تنفيذ سريع بطلب المستخدم: أحدث الأعداد المتاحة من 1443هـ إلى 1447هـ فقط.
TARGET_ISSUE_INDICES = {25, 27, 28, 29, 30, 31, 32}

SCHEMA = {
    'name': 'ksu_journal_toc_extraction',
    'strict': True,
    'schema': {
        'type': 'object',
        'properties': {
            'contains_table_of_contents': {'type': 'boolean'},
            'articles': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'title': {'type': 'string'},
                        'author': {'type': 'string'},
                        'start_page': {'type': 'string'},
                    },
                    'required': ['title', 'author', 'start_page'],
                    'additionalProperties': False,
                },
            },
            'uncertainty_note': {'type': 'string'},
        },
        'required': ['contains_table_of_contents', 'articles', 'uncertainty_note'],
        'additionalProperties': False,
    },
}
SYSTEM = (
    'You are a meticulous Arabic academic-journal bibliographer. Extract only the '\
    'scholarly article records visibly listed in the supplied table-of-contents pages. '\
    'Keep Arabic text faithful to the image, preserve punctuation, and never invent '\
    'a missing title or author. Exclude editorial boards, publication rules, forewords, '\
    'index headers, page-number lines, and other non-article text. Return an empty '\
    'string for an unreadable author or start page. If none of the pages has a table '\
    'of contents, set contains_table_of_contents to false and return no articles.'
)


def pages_in_pdf(pdf: Path) -> int:
    output = subprocess.run(['pdfinfo', str(pdf)], check=True, text=True, capture_output=True).stdout
    hit = re.search(r'^Pages:\s+(\d+)$', output, re.M)
    if not hit:
        raise RuntimeError(f'Cannot determine page count for {pdf.name}')
    return int(hit.group(1))


def render(pdf: Path, issue_id: str, wanted: list[int]) -> list[Path]:
    issue_dir = RENDER_DIR / issue_id
    issue_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for p in wanted:
        output = issue_dir / f'p{p}'
        image = issue_dir / f'p{p}.jpg'
        if not image.exists():
            subprocess.run([
                'pdftoppm', '-f', str(p), '-l', str(p), '-r', '220', '-jpeg',
                '-jpegopt', 'quality=82', '-singlefile', str(pdf), str(output),
            ], check=True, capture_output=True)
        paths.append(image)
    return paths


def image_url(path: Path) -> str:
    return 'data:image/jpeg;base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


def call_model(images: list[Path]) -> dict:
    client = OpenAI()
    content = [{'type': 'text', 'text': (
        'These are consecutive opening pages of one issue of the Journal of King Saud '\
        'University: Law & Political Science. Identify every article from the table of '\
        'contents if present. Do not mix entries from other pages.'
    )}]
    content += [{'type': 'image_url', 'image_url': {'url': image_url(path), 'detail': 'high'}} for path in images]
    last: Exception | None = None
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                max_completion_tokens=8000,
                messages=[{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': content}],
                response_format={'type': 'json_schema', 'json_schema': SCHEMA},
            )
            return json.loads(response.choices[0].message.content)
        except Exception as exc:
            last = exc
            time.sleep(2 ** attempt)
    raise RuntimeError(f'LLM extraction failed: {last}')


def clean_title(value: str) -> str:
    value = re.sub(r'\s+', ' ', value).strip(' \t\n-–—،')
    return value


def extract(issue: dict) -> dict:
    pdf = ISSUES_DIR / issue['local_filename']
    total_pages = pages_in_pdf(pdf)
    preferred = [p for p in (6, 7, 8) if p <= total_pages]
    result = call_model(render(pdf, f'{issue["archive_index"]:02d}', preferred))
    used_pages = preferred
    if not result['contains_table_of_contents'] or not result['articles']:
        fallback = [p for p in (4, 5) if p <= total_pages]
        if fallback:
            result = call_model(render(pdf, f'{issue["archive_index"]:02d}', fallback))
            used_pages = fallback
    articles = []
    seen = set()
    for article in result['articles']:
        title = clean_title(article['title'])
        if not title or title in seen:
            continue
        seen.add(title)
        articles.append({
            'title': title,
            'author': clean_title(article['author']),
            'start_page': clean_title(article['start_page']),
        })
    return {
        'archive_index': issue['archive_index'],
        'issue_label': issue['issue_label'],
        'official_issue_url': issue['official_issue_url'],
        'page_count': total_pages,
        'toc_pages_examined': used_pages,
        'contains_table_of_contents': result['contains_table_of_contents'],
        'uncertainty_note': result['uncertainty_note'],
        'articles': articles,
    }


def main() -> None:
    doc = json.loads(MANIFEST.read_text(encoding='utf-8'))
    available = [
        x for x in doc['issues']
        if x['archive_index'] in TARGET_ISSUE_INDICES and x.get('download_status') in {'downloaded', 'cached'}
    ]
    if {x['archive_index'] for x in available} != TARGET_ISSUE_INDICES:
        raise RuntimeError('One or more selected recent issue PDFs are unavailable')
    unavailable = [
        {'archive_index': x['archive_index'], 'issue_label': x['issue_label'],
         'official_issue_url': x['official_issue_url'], 'error': x.get('retry_error') or x.get('error') or ''}
        for x in doc['issues']
        if x['archive_index'] in TARGET_ISSUE_INDICES and x.get('download_status') not in {'downloaded', 'cached'}
    ]
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        future_to_issue = {executor.submit(extract, issue): issue for issue in available}
        for n, future in enumerate(concurrent.futures.as_completed(future_to_issue), 1):
            issue = future_to_issue[future]
            try:
                row = future.result()
                rows.append(row)
                print(f'[{n}/{len(available)}] issue {issue["archive_index"]}: {len(row["articles"])} articles', flush=True)
            except Exception as exc:
                failures.append({'archive_index': issue['archive_index'], 'issue_label': issue['issue_label'], 'error': f'{type(exc).__name__}: {exc}'})
                print(f'[{n}/{len(available)}] issue {issue["archive_index"]}: FAILED {type(exc).__name__}', flush=True)
    rows.sort(key=lambda x: x['archive_index'])
    out = {
        'source': 'مجلة جامعة الملك سعود للحقوق والعلوم السياسية',
        'source_archive_url': 'https://clps.ksu.edu.sa/en/node/1070',
        'extracted_at_utc': datetime.now(timezone.utc).isoformat(),
        'requested_issue_indices': sorted(TARGET_ISSUE_INDICES),
        'available_issue_count': len(available),
        'unavailable_issues': unavailable,
        'issues': rows,
        'failures': failures,
        'article_count_raw': sum(len(x['articles']) for x in rows),
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'issues': len(rows), 'failures': len(failures), 'article_count_raw': out['article_count_raw']}, ensure_ascii=False), flush=True)
    if failures:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
