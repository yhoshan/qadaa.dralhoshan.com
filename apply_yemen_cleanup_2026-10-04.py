#!/usr/bin/env python3
"""Apply only the audited Yemen-removal manifest by exact record ID."""
from __future__ import annotations
import hashlib,json
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ITEMS=ROOT/'items.json'; PUBLIC_ITEMS=ROOT/'client/public/items.json'
STATS=ROOT/'stats.json'; PUBLIC_STATS=ROOT/'client/public/stats.json'
HOOK=ROOT/'client/src/hooks/useItems.ts'
MANIFEST=ROOT/'yemen_final_removal_manifest_2026-10-04.json'
OUT=ROOT/'yemen_cleanup_2026-10-04_execution.json'
OLD_TOKEN='qadaa-explicit-47-removals-2026-10-04'
NEW_TOKEN='qadaa-yemen-cleanup-2026-10-04'

def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def counts(v):return dict(sorted(Counter(x for x in v if x).items(),key=lambda x:(-x[1],x[0])))
def main():
    m=json.loads(MANIFEST.read_text(encoding='utf8'))
    targets=[x['id'] for x in m['records']]
    if m['catalogue_total_before']!=46494 or m['removal_count']!=642 or len(targets)!=642 or len(set(targets))!=642:raise RuntimeError('Manifest integrity failure')
    items=json.loads(ITEMS.read_text(encoding='utf8')); public=json.loads(PUBLIC_ITEMS.read_text(encoding='utf8'))
    if items!=public:raise RuntimeError('Root/public items mismatch before cleanup')
    if len(items)!=46494:raise RuntimeError(f'Expected 46494 before cleanup, found {len(items)}')
    before={x['id']:x for x in items}
    if len(before)!=len(items):raise RuntimeError('Duplicate IDs before cleanup')
    missing=[x for x in targets if x not in before]
    if missing:raise RuntimeError(f'Manifest IDs missing: {missing}')
    targetset=set(targets); removed=[before[x] for x in targets]; after=[x for x in items if x['id'] not in targetset]; after_by={x['id']:x for x in after}
    if len(after)!=45852 or len(after)!=len(items)-len(targetset):raise RuntimeError('Unexpected post-cleanup total')
    if len(after_by)!=len(after) or any(i in after_by for i in targets):raise RuntimeError('Post-cleanup ID integrity failure')
    for ident,row in before.items():
        if ident not in targetset and after_by.get(ident)!=row:raise RuntimeError(f'Non-target modified: {ident}')
    stats=json.loads(STATS.read_text(encoding='utf8'));stats['total_items']=len(after)
    if 'total' in stats:stats['total']=len(after)
    stats['categories']=counts(str(x.get('category','')) for x in after)
    stats['sources']=counts(str(x.get('source','')) for x in after)
    stats['material_types']=counts(str(x.get('material_type','')) for x in after)
    stats['file_types']=counts(str(x.get('file_type','')) for x in after)
    stats['featured_count']=sum(bool(x.get('is_featured')) for x in after)
    stats['with_download_links']=sum(int(x.get('download_links_count') or 0)>0 for x in after)
    write(ITEMS,after);write(PUBLIC_ITEMS,after);write(STATS,stats);write(PUBLIC_STATS,stats)
    h=HOOK.read_text(encoding='utf8')
    if OLD_TOKEN not in h:raise RuntimeError('Expected prior cache token missing')
    HOOK.write_text(h.replace(OLD_TOKEN,NEW_TOKEN),encoding='utf8')
    report={'operation':'yemen_cleanup_exact_id_only','executed_at_utc':datetime.now(timezone.utc).isoformat(),'before_total':len(items),'manifest_removal_count':len(targets),'removed_total':len(removed),'after_total':len(after),'removed_by_source':dict(Counter(x['source'] for x in removed)),'removed_ids':targets,'cache_token':NEW_TOKEN,'items_sha256':sha(ITEMS),'public_items_sha256':sha(PUBLIC_ITEMS),'stats_sha256':sha(STATS),'public_stats_sha256':sha(PUBLIC_STATS)}
    write(OUT,report);print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
