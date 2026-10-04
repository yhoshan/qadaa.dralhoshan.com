#!/usr/bin/env python3
"""Remove the one confirmed remaining Yemen journal record by exact ID only."""
from __future__ import annotations
import hashlib,json
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
TARGET='journal_link_87e8d4e152f2cf24'
EXPECTED_SOURCE='فهرس المجلات المتخصصة — اليمن'
FILES=[ROOT/'items.json',ROOT/'client/public/items.json']
STATS=[ROOT/'stats.json',ROOT/'client/public/stats.json']
HOOK=ROOT/'client/src/hooks/useItems.ts';OUT=ROOT/'yemen_residual_journal_2026-10-04_execution.json'
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cnt(vals):return dict(sorted(Counter(v for v in vals if v).items(),key=lambda t:(-t[1],t[0])))
def main():
 items=json.loads(FILES[0].read_text(encoding='utf8'));public=json.loads(FILES[1].read_text(encoding='utf8'))
 if items!=public or len(items)!=45852:raise RuntimeError('Unexpected pre-deletion state')
 before={x['id']:x for x in items}
 if TARGET not in before or before[TARGET].get('source')!=EXPECTED_SOURCE:raise RuntimeError('Target identity failed')
 after=[x for x in items if x['id']!=TARGET];after_by={x['id']:x for x in after}
 if len(after)!=45851 or TARGET in after_by:raise RuntimeError('Target delete failed')
 if any(after_by[k]!=v for k,v in before.items() if k!=TARGET):raise RuntimeError('Non-target changed')
 stats=json.loads(STATS[0].read_text(encoding='utf8'));stats['total_items']=len(after)
 if 'total' in stats:stats['total']=len(after)
 stats['categories']=cnt(str(x.get('category','')) for x in after);stats['sources']=cnt(str(x.get('source','')) for x in after);stats['material_types']=cnt(str(x.get('material_type','')) for x in after);stats['file_types']=cnt(str(x.get('file_type','')) for x in after);stats['featured_count']=sum(bool(x.get('is_featured')) for x in after);stats['with_download_links']=sum(int(x.get('download_links_count') or 0)>0 for x in after)
 for p in FILES:dump(p,after)
 for p in STATS:dump(p,stats)
 h=HOOK.read_text(encoding='utf8');old='qadaa-yemen-cleanup-2026-10-04';new='qadaa-yemen-cleanup-final-2026-10-04'
 if old not in h:raise RuntimeError('Cache token mismatch')
 HOOK.write_text(h.replace(old,new),encoding='utf8')
 result={'operation':'residual_yemen_journal_exact_id_removal','executed_at_utc':datetime.now(timezone.utc).isoformat(),'removed_id':TARGET,'before_total':len(items),'after_total':len(after),'non_targets_unchanged':True,'cache_token':new,'items_sha256':sha(FILES[0]),'public_items_sha256':sha(FILES[1]),'stats_sha256':sha(STATS[0]),'public_stats_sha256':sha(STATS[1])};dump(OUT,result);print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
