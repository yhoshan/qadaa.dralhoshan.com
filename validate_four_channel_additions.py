#!/usr/bin/env python3
"""Validate the four-channel addition without modifying the catalogue."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / 'backups' / 'four_channels_2026-10-03'
MANIFEST = ROOT / 'qadaiyat_and_hadeeth_2026-10-03_precheck' / 'final_addition_manifest.json'
EXPECTED = {
    'before': 18340,
    'added': 1049,
    'after': 19389,
    'sources': {
        'قضائيات': 511,
        'حديث القانون — المنصة القانونية للمحامين': 288,
        'مكتبة المحامية رباب المعبي': 199,
        'المحامية وجدان الزهراني ⚖️': 51,
    },
}


def load(path: Path): return json.loads(path.read_text(encoding='utf-8'))
def counts(items, key): return dict(sorted(Counter(str(x.get(key) or '') for x in items if x.get(key)).items(), key=lambda pair: (-pair[1], pair[0])))


def main() -> None:
    before = load(BACKUP / 'items_before.json')
    after = load(ROOT / 'items.json')
    public = load(ROOT / 'client/public/items.json')
    stats = load(ROOT / 'stats.json')
    public_stats = load(ROOT / 'client/public/stats.json')
    expected_additions = load(MANIFEST)
    assert len(before) == EXPECTED['before']
    assert len(after) == len(public) == EXPECTED['after']
    assert after == public
    assert len(expected_additions) == EXPECTED['added']
    before_by_id = {str(x['id']): x for x in before}
    after_by_id = {str(x['id']): x for x in after}
    added_ids = {str(x['id']) for x in expected_additions}
    assert len(before_by_id) == len(before) and len(after_by_id) == len(after)
    assert set(after_by_id) - set(before_by_id) == added_ids
    assert all(after_by_id[item_id] == item for item_id, item in before_by_id.items())
    assert all(after_by_id[item['id']] == item for item in expected_additions)
    assert stats == public_stats
    assert stats['total_items'] == stats['total'] == stats['books_count'] == EXPECTED['after']
    assert stats['categories'] == counts(after, 'category')
    assert stats['sources'] == counts(after, 'source')
    assert stats['material_types'] == counts(after, 'material_type')
    assert stats['file_types'] == counts(after, 'file_type')
    assert stats['featured_count'] == sum(bool(x.get('is_featured')) for x in after)
    assert stats['with_download_links'] == sum(int(x.get('download_links_count') or 0) > 0 for x in after)
    actual_sources = {source: stats['sources'].get(source, 0) for source in EXPECTED['sources']}
    assert actual_sources == EXPECTED['sources']
    assert all(str(x['link_telegram']).startswith('https://t.me/') for x in expected_additions)
    hook = (ROOT / 'client/src/hooks/useItems.ts').read_text(encoding='utf-8')
    assert hook.count('qadaa-four-channels-2026-10-03') == 2
    result = {
        'valid': True,
        'before_total': len(before),
        'added_total': len(added_ids),
        'after_total': len(after),
        'sources_added': actual_sources,
        'items_sha256': hashlib.sha256((ROOT / 'items.json').read_bytes()).hexdigest(),
        'stats_sha256': hashlib.sha256((ROOT / 'stats.json').read_bytes()).hexdigest(),
        'checks': {
            'only_manifest_ids_added': True,
            'existing_records_unchanged': True,
            'main_public_items_equal': True,
            'main_public_stats_equal': True,
            'all_ids_unique': True,
            'stats_rebuilt': True,
            'cache_token_updated': True,
        },
    }
    (ROOT / 'four_channel_additions_2026-10-03_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__ == '__main__': main()
