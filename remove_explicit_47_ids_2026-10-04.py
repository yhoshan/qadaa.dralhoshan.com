#!/usr/bin/env python3
"""Delete only the 47 explicit IDs supplied by the user, then rebuild derived JSON.
No semantic or title-based deletion is performed here.
"""
from __future__ import annotations
import hashlib, json, re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent
ITEMS=ROOT/'items.json'; PUBLIC_ITEMS=ROOT/'client/public/items.json'
STATS=ROOT/'stats.json'; PUBLIC_STATS=ROOT/'client/public/stats.json'
HOOK=ROOT/'client/src/hooks/useItems.ts'
REQUEST=Path('/home/ubuntu/upload/pasted_content.txt')
EXEC=ROOT/'explicit_47_ids_2026-10-04_execution.json'
ALLOWED={'مكتبة القاضي محمد الأهدل القانونية والقضائية','مكتبة القاضي صلاح سيف القانونية والقضائية'}
OLD_TOKEN='qadaa-qadi-libraries-2026-10-03'
NEW_TOKEN='qadaa-explicit-47-removals-2026-10-04'


def digest(path: Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path: Path, value)->None:
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def count(values):
    return dict(sorted(Counter(v for v in values if v).items(),key=lambda x:(-x[1],x[0])))

def main():
    requested=re.findall(r'`([^`]+)`', REQUEST.read_text(encoding='utf8'))
    if len(requested)!=47 or len(set(requested))!=47:
        raise RuntimeError(f'Expected 47 unique requested IDs; found {len(requested)} / {len(set(requested))}')
    items=json.loads(ITEMS.read_text(encoding='utf8'))
    public=json.loads(PUBLIC_ITEMS.read_text(encoding='utf8'))
    if items!=public: raise RuntimeError('Root and public items are not identical before deletion')
    if len(items)!=46541: raise RuntimeError(f'Expected 46541 records before deletion; found {len(items)}')
    before_by_id={x['id']:x for x in items}
    if len(before_by_id)!=len(items): raise RuntimeError('Duplicate IDs before deletion')
    missing=[x for x in requested if x not in before_by_id]
    if missing: raise RuntimeError(f'Requested IDs missing: {missing}')
    wrong_source=[x for x in requested if before_by_id[x].get('source') not in ALLOWED]
    if wrong_source: raise RuntimeError(f'Unexpected source for IDs: {wrong_source}')
    removed=[before_by_id[x] for x in requested]
    after=[x for x in items if x['id'] not in set(requested)]
    after_by_id={x['id']:x for x in after}
    if len(after)!=len(items)-47 or len(after_by_id)!=len(after): raise RuntimeError('Unexpected post-deletion count or IDs')
    if any(x in after_by_id for x in requested): raise RuntimeError('At least one requested ID remains')
    for ident, before in before_by_id.items():
        if ident not in set(requested) and after_by_id.get(ident)!=before:
            raise RuntimeError(f'Non-target record modified: {ident}')
    stats=json.loads(STATS.read_text(encoding='utf8'))
    stats['total_items']=len(after)
    if 'total' in stats: stats['total']=len(after)
    stats['categories']=count(str(x.get('category','')) for x in after)
    stats['sources']=count(str(x.get('source','')) for x in after)
    stats['material_types']=count(str(x.get('material_type','')) for x in after)
    stats['file_types']=count(str(x.get('file_type','')) for x in after)
    stats['featured_count']=sum(bool(x.get('is_featured')) for x in after)
    stats['with_download_links']=sum(int(x.get('download_links_count') or 0)>0 for x in after)
    write(ITEMS,after); write(PUBLIC_ITEMS,after); write(STATS,stats); write(PUBLIC_STATS,stats)
    hook=HOOK.read_text(encoding='utf8')
    if OLD_TOKEN not in hook: raise RuntimeError(f'Old cache token not found: {OLD_TOKEN}')
    HOOK.write_text(hook.replace(OLD_TOKEN,NEW_TOKEN),encoding='utf8')
    result={
      'operation':'explicit_id_deletion_only',
      'executed_at_utc':datetime.now(timezone.utc).isoformat(),
      'requested_count':47,'found_count':47,'removed_count':47,
      'before_total':len(items),'after_total':len(after),
      'removed_by_source':dict(Counter(x['source'] for x in removed)),
      'removed_ids':requested,
      'removed_records':[{'id':x['id'],'title':x['title'],'source':x['source']} for x in removed],
      'cache_token':NEW_TOKEN,
      'items_sha256':digest(ITEMS),'public_items_sha256':digest(PUBLIC_ITEMS),
      'stats_sha256':digest(STATS),'public_stats_sha256':digest(PUBLIC_STATS)
    }
    write(EXEC,result)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
