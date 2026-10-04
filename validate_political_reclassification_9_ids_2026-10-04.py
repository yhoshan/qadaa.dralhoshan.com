#!/usr/bin/env python3
"""Post-deletion integrity validation for exactly nine approved ID deletions."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / 'backups/political_reclassification_9_ids_2026-10-04'
RESULT = ROOT / 'political_reclassification_9_ids_2026-10-04_validation.json'
TARGETS = [
    'archive_no-law-no-rights-state','great_law_5423','qadi_ahdal_107698',
    'qadi_ahdal_14977','qadi_ahdal_31900','qadi_ahdal_53906',
    'qadi_ahdal_58456','qadi_ahdal_58548','qadi_ahdal_79295',
]
CACHE = 'qadaa-political-reclassification-nine-removals-2026-10-04'

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def counter(values):
    return dict(sorted(Counter(v for v in values if v).items(), key=lambda x:(-x[1],x[0])))

def main():
    root_items=json.loads((ROOT/'items.json').read_text(encoding='utf-8'))
    public_items=json.loads((ROOT/'client/public/items.json').read_text(encoding='utf-8'))
    before=json.loads((BACKUP/'items_before.json').read_text(encoding='utf-8'))
    root_stats=json.loads((ROOT/'stats.json').read_text(encoding='utf-8'))
    public_stats=json.loads((ROOT/'client/public/stats.json').read_text(encoding='utf-8'))
    assert root_items == public_items, 'Root/public items mismatch'
    assert root_stats == public_stats, 'Root/public stats mismatch'
    assert len(before)==45838, f'Bad backup count: {len(before)}'
    assert len(root_items)==45829, f'Bad final count: {len(root_items)}'
    by_before={x['id']:x for x in before}; by_after={x['id']:x for x in root_items}
    assert len(by_before)==len(before), 'Duplicate IDs in backup'
    assert len(by_after)==len(root_items), 'Duplicate IDs after deletion'
    assert all(i in by_before for i in TARGETS), 'Target missing from backup'
    assert all(i not in by_after for i in TARGETS), 'A target remains after deletion'
    untouched=[i for i in by_before if i not in TARGETS]
    changed=[i for i in untouched if by_after.get(i)!=by_before[i]]
    assert not changed, f'Changed non-target records: {changed[:10]}'
    assert root_stats.get('total_items')==45829, 'Stats total does not match items'
    assert root_stats.get('categories') == counter([str(x.get('category') or '') for x in root_items]), 'Category stats mismatch'
    assert root_stats.get('sources') == counter([str(x.get('source') or '') for x in root_items]), 'Source stats mismatch'
    assert root_stats.get('material_types') == counter([str(x.get('material_type') or '') for x in root_items]), 'Material-type stats mismatch'
    assert root_stats.get('file_types') == counter([str(x.get('file_type') or '') for x in root_items]), 'File-type stats mismatch'
    assert root_stats.get('featured_count') == sum(bool(x.get('is_featured')) for x in root_items), 'Featured stats mismatch'
    assert root_stats.get('with_download_links') == sum(int(x.get('download_links_count') or 0)>0 for x in root_items), 'Download stats mismatch'
    hero=[root_stats.get(k) for k in ('qadaa_count','nizam_count','mohama_count')]
    assert all(isinstance(x,int) for x in hero), f'Missing hero counts: {hero}'
    assert sum(hero)==45829, f'Hero total mismatch: {hero}'
    hook=(ROOT/'client/src/hooks/useItems.ts').read_text(encoding='utf-8')
    assert hook.count(CACHE)==2, 'Cache token was not updated exactly twice'
    result={
       'validated_at_utc':datetime.now(timezone.utc).isoformat(),
       'status':'passed', 'before_total':len(before),'after_total':len(root_items),
       'removed_count':len(TARGETS),'remaining_targets':[i for i in TARGETS if i in by_after],
       'non_target_records_changed':len(changed),
       'duplicate_ids_after':len(root_items)-len(by_after),
       'root_public_items_identical':True,'root_public_stats_identical':True,
       'hero_counts':{'qadaa':hero[0],'nizam':hero[1],'mohama':hero[2]},
       'cache_token':CACHE,
       'items_sha256':sha(ROOT/'items.json'),'stats_sha256':sha(ROOT/'stats.json')
    }
    RESULT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
