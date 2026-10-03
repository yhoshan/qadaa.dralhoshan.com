#!/usr/bin/env python3
"""Reliably retry official KSU journal issue PDFs after transient transfers."""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

WORKDIR = Path('/home/ubuntu/ksu-law-journal-archive-2026-10-03')
MANIFEST = WORKDIR / 'archive_manifest.json'
ISSUES = WORKDIR / 'issues'


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def fetch(issue: dict) -> None:
    target = ISSUES / issue['local_filename']
    temp = target.with_suffix('.retry')
    temp.unlink(missing_ok=True)
    command = [
        'curl', '--fail', '--location', '--silent', '--show-error',
        '--retry', '8', '--retry-all-errors', '--retry-delay', '3',
        '--connect-timeout', '20', '--max-time', '600',
        '--user-agent', 'Makanez-Catalogue-Research/1.0 (+https://qadaa.dralhoshan.com)',
        '--output', str(temp), issue['official_issue_url'],
    ]
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode or not temp.exists() or temp.stat().st_size < 1024 or temp.read_bytes()[:4] != b'%PDF':
        temp.unlink(missing_ok=True)
        issue.update({'download_status': 'failed', 'retry_error': (result.stderr or result.stdout or f'curl exit {result.returncode}').strip()})
        return
    temp.replace(target)
    issue.update({
        'download_status': 'downloaded',
        'local_path': str(target),
        'bytes': target.stat().st_size,
        'sha256': sha256(target),
        'retried_at_utc': datetime.now(timezone.utc).isoformat(),
    })


def main() -> None:
    doc = json.loads(MANIFEST.read_text(encoding='utf-8'))
    failed = [x for x in doc['issues'] if x.get('download_status') == 'failed']
    for position, issue in enumerate(failed, 1):
        print(f'[{position}/{len(failed)}] {issue["issue_label"]}', flush=True)
        fetch(issue)
        print(f'  {issue["download_status"]}', flush=True)
        MANIFEST.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    doc['downloaded_count'] = sum(x.get('download_status') in {'downloaded', 'cached'} for x in doc['issues'])
    doc['failed_count'] = len(doc['issues']) - doc['downloaded_count']
    doc['last_retry_at_utc'] = datetime.now(timezone.utc).isoformat()
    MANIFEST.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: doc[k] for k in ('issue_count', 'downloaded_count', 'failed_count')}, ensure_ascii=False), flush=True)
    if doc['failed_count']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
