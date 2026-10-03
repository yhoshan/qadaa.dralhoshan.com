#!/usr/bin/env python3
"""Apply the already-reviewed four-channel manifest safely and deterministically."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / 'qadaiyat_and_hadeeth_2026-10-03_precheck' / 'final_addition_manifest.json'
ITEMS = ROOT / 'items.json'
PUBLIC_ITEMS = ROOT / 'client' / 'public' / 'items.json'
HOOK = ROOT / 'client' / 'src' / 'hooks' / 'useItems.ts'
REPORT = ROOT / 'four_channel_additions_2026-10-03_execution.json'
EXPECTED_BEFORE = 18340
EXPECTED_ADD = 1049
CACHE_FROM = 'qadaa-tabseet-civil-articles-2026-10-02'
CACHE_TO = 'qadaa-four-channels-2026-10-03'


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    before_bytes = ITEMS.read_bytes()
    hook_text = HOOK.read_text(encoding='utf-8')
    if before_bytes != PUBLIC_ITEMS.read_bytes():
        raise SystemExit('Main and public items files differ before integration')
    items = json.loads(before_bytes)
    additions = json.loads(MANIFEST.read_text(encoding='utf-8'))
    if len(items) != EXPECTED_BEFORE:
        raise SystemExit(f'Expected {EXPECTED_BEFORE} current items, found {len(items)}')
    if len(additions) != EXPECTED_ADD:
        raise SystemExit(f'Expected {EXPECTED_ADD} additions, found {len(additions)}')
    ids = [str(x.get('id', '')) for x in items]
    add_ids = [str(x.get('id', '')) for x in additions]
    if any(not value for value in add_ids) or len(add_ids) != len(set(add_ids)):
        raise SystemExit('Addition manifest has empty or duplicate IDs')
    if set(ids) & set(add_ids):
        raise SystemExit('Addition IDs collide with current items')
    required = {'id','title','source','category','material_type','file_type','link_telegram','download_links_count'}
    for entry in additions:
        missing = sorted(key for key in required if key not in entry)
        if missing or not str(entry['title']).strip() or not str(entry['source']).strip():
            raise SystemExit(f'Invalid addition {entry.get("id")}: missing {missing}')
        url = str(entry['link_telegram'])
        if not re.fullmatch(r'https://t\.me/(?:[A-Za-z0-9_]+|c/\d+)/\d+', url):
            raise SystemExit(f'Invalid Telegram URL in {entry["id"]}: {url}')
    if hook_text.count(CACHE_FROM) != 2:
        raise SystemExit(f'Expected exactly two cache version tokens {CACHE_FROM}')

    combined = items + additions
    after = (json.dumps(combined, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    ITEMS.write_bytes(after)
    PUBLIC_ITEMS.write_bytes(after)

    HOOK.write_text(hook_text.replace(CACHE_FROM, CACHE_TO), encoding='utf-8')

    report = {
        'executed_at_utc': datetime.now(timezone.utc).isoformat(),
        'before_total': len(items),
        'added_total': len(additions),
        'after_total': len(combined),
        'before_items_sha256': sha(before_bytes),
        'after_items_sha256': sha(after),
        'manifest_sha256': sha(MANIFEST.read_bytes()),
        'cache_token_from': CACHE_FROM,
        'cache_token_to': CACHE_TO,
        'source_counts': {source: sum(x['source'] == source for x in additions) for source in sorted({x['source'] for x in additions})},
        'added_ids_sha256': sha(('\n'.join(add_ids)+'\n').encode()),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
