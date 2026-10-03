#!/usr/bin/env python3
"""Guarded integration of the three fully screened legal-library candidate sources."""
from __future__ import annotations
import hashlib,json
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ITEMS=ROOT/'items.json'; PUBLIC_ITEMS=ROOT/'client/public/items.json'
STATS=ROOT/'stats.json'; PUBLIC_STATS=ROOT/'client/public/stats.json'
HOOK=ROOT/'client/src/hooks/useItems.ts'
CAND=ROOT/'qadi_libraries_2026-10-03_candidates_deduped.json'
EXEC=ROOT/'qadi_libraries_2026-10-03_execution.json'
BEFORE=20080; ADD=26461; TOKEN_OLD='qadaa-jtc-qiyam-2026-10-03'; TOKEN_NEW='qadaa-qadi-libraries-2026-10-03'
FIELDS=('id','title','author','investigator','publisher','year','link_telegram','link_drive','link_direct','source','category','material_type','file_type','file_size','pages_count','is_featured','download_links_count')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def counts(values):return dict(sorted(Counter(v for v in values if v).items(),key=lambda t:(-t[1],t[0])))
def main():
 items=json.loads(ITEMS.read_text(encoding='utf8')); candidates=json.loads(CAND.read_text(encoding='utf8'))
 if not isinstance(items,list) or not isinstance(candidates,list):raise RuntimeError('Expected list JSON structures')
 if len(items)!=BEFORE:raise RuntimeError(f'Expected {BEFORE} records before integration; found {len(items)}')
 if len(candidates)!=ADD:raise RuntimeError(f'Expected {ADD} candidates; found {len(candidates)}')
 records=[{k:x.get(k,'') for k in FIELDS} for x in candidates]
 ids=[str(x['id']) for x in records]
 if len(ids)!=len(set(ids)):raise RuntimeError('Duplicate IDs in candidate set')
 existing_ids={str(x.get('id','')) for x in items}
 if set(ids)&existing_ids:raise RuntimeError('Candidate ID collision with current catalogue')
 allowed={'تسهيل الأنظمة','مكتبة القاضي محمد الأهدل القانونية والقضائية','مكتبة القاضي صلاح سيف القانونية والقضائية'}
 if {x['source'] for x in records}-allowed:raise RuntimeError('Unexpected candidate source')
 if any(not x['title'] or not x['link_telegram'].startswith('https://t.me/') or x['download_links_count']!=1 for x in records):raise RuntimeError('Missing title, public Telegram link, or link count')
 links=[x['link_telegram'] for x in records]
 if len(links)!=len(set(links)):raise RuntimeError('Duplicate public Telegram links in candidate set')
 existing_links={str(x.get(k,'')) for x in items for k in ('link_telegram','link_drive','link_direct') if x.get(k)}
 if set(links)&existing_links:raise RuntimeError('Candidate link collision with existing catalogue')
 before_by_id={x['id']:x for x in items}; after=items+records;after_by_id={x['id']:x for x in after}
 if len(after)!=BEFORE+ADD or len(after_by_id)!=len(after):raise RuntimeError('Post-addition total or uniqueness validation failed')
 if any(after_by_id[k]!=v for k,v in before_by_id.items()):raise RuntimeError('Existing records changed unexpectedly')
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
 if TOKEN_OLD not in h:raise RuntimeError(f'Expected cache token {TOKEN_OLD} absent')
 HOOK.write_text(h.replace(TOKEN_OLD,TOKEN_NEW),encoding='utf8')
 result={'operation':'add_qadi_libraries_2026_10_03','executed_at':datetime.now(timezone.utc).isoformat(),'before_total':BEFORE,'added_total':ADD,'after_total':len(after),'added_by_source':dict(Counter(x['source'] for x in records)),'first_added_id':ids[0],'last_added_id':ids[-1],'cache_token':TOKEN_NEW,'items_sha256':sha(ITEMS),'public_items_sha256':sha(PUBLIC_ITEMS),'stats_sha256':sha(STATS),'public_stats_sha256':sha(PUBLIC_STATS)}
 write(EXEC,result);print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
