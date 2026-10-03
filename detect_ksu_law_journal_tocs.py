#!/usr/bin/env python3
"""Locate Arabic tables of contents in official KSU law journal issue PDFs.

The script renders only the opening pages of each issue and uses local Arabic OCR
for detection. It produces source-review artifacts outside the web catalogue data.
"""
from __future__ import annotations

import concurrent.futures
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

WORKDIR = Path('/home/ubuntu/ksu-law-journal-archive-2026-10-03')
MANIFEST = WORKDIR / 'archive_manifest.json'
ISSUES = WORKDIR / 'issues'
OUT = WORKDIR / 'toc-detection'
OUT_IMAGES = OUT / 'images'
RESULT = WORKDIR / 'toc_detection.json'
MAX_SCAN_PAGES = 18
WORKERS = 3


def run(command: list[str]) -> str:
    return subprocess.run(command, check=True, text=True, capture_output=True).stdout


def page_count(pdf: Path) -> int:
    text = run(['pdfinfo', str(pdf)])
    match = re.search(r'^Pages:\s+(\d+)$', text, re.M)
    if not match:
        raise RuntimeError(f'No page count in {pdf}')
    return int(match.group(1))


def ocr(image: Path) -> str:
    result = subprocess.run(
        ['tesseract', str(image), 'stdout', '-l', 'ara', '--psm', '6'],
        text=True, capture_output=True, check=False,
    )
    return result.stdout.replace('\x0c', '').strip()


def detect(issue: dict) -> dict:
    pdf = ISSUES / issue['local_filename']
    count = page_count(pdf)
    scan = min(MAX_SCAN_PAGES, count)
    issue_dir = OUT_IMAGES / f"{issue['archive_index']:02d}"
    shutil.rmtree(issue_dir, ignore_errors=True)
    issue_dir.mkdir(parents=True, exist_ok=True)
    prefix = issue_dir / 'page'
    subprocess.run([
        'pdftoppm', '-f', '1', '-l', str(scan), '-r', '150', '-jpeg',
        '-jpegopt', 'quality=72', str(pdf), str(prefix),
    ], check=True, capture_output=True)
    pages = sorted(issue_dir.glob('page-*.jpg'), key=lambda p: int(re.search(r'-(\d+)\.jpg$', p.name).group(1)))
    hits = []
    snippets = {}
    for image in pages:
        number = int(re.search(r'-(\d+)\.jpg$', image.name).group(1))
        text = ocr(image)
        snippets[str(number)] = re.sub(r'\s+', ' ', text)[:1000]
        # OCR can confuse the final letters in "المحتويات". The stable prefix is enough.
        if re.search(r'المحت|محتو|محتب|محتب', text.replace('ـ', '')):
            hits.append(number)
    selected = sorted({page for hit in hits for page in range(hit, min(hit + 3, count + 1))})
    return {
        'archive_index': issue['archive_index'],
        'issue_label': issue['issue_label'],
        'official_issue_url': issue['official_issue_url'],
        'pdf_path': str(pdf),
        'page_count': count,
        'scanned_pages': scan,
        'toc_marker_pages': hits,
        'selected_toc_pages': selected,
        'ocr_snippets': snippets,
    }


def main() -> None:
    doc = json.loads(MANIFEST.read_text(encoding='utf-8'))
    issues = [x for x in doc['issues'] if x.get('download_status') in {'downloaded', 'cached'}]
    unavailable = [
        {
            'archive_index': x['archive_index'],
            'issue_label': x['issue_label'],
            'official_issue_url': x['official_issue_url'],
            'download_status': x.get('download_status'),
            'error': x.get('retry_error') or x.get('error') or '',
        }
        for x in doc['issues'] if x.get('download_status') not in {'downloaded', 'cached'}
    ]
    OUT.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
        records = list(executor.map(detect, issues))
    missing = [x['archive_index'] for x in records if not x['toc_marker_pages']]
    result = {
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'archive_issue_count': doc['issue_count'],
        'issue_count': len(records),
        'unavailable_issues': unavailable,
        'issues_without_toc_marker': missing,
        'issues': records,
    }
    RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'issue_count': len(records), 'unavailable_count': len(unavailable), 'without_marker': missing}, ensure_ascii=False))
    if missing:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
