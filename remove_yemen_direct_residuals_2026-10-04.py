#!/usr/bin/env python3
"""Remove 13 post-audit direct Yemen records by their explicit IDs only."""
from __future__ import annotations
import hashlib,json
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
TARGETS=json.loads((ROOT/'yemen_direct_residual_ids_2026-10-04.json').read_text(encoding='utf8'))
FILES=[ROOT/'items.json',ROOT/'client/public/items.json'];STAT=[ROOT/'stats.json',ROOT/'client/public/stats.json'];HOOK=ROOT/'client/src/hooks/useItems.ts';OUT=ROOT/'yemen_direct_residuals_2026-10-04_execution.json'
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cnt(v):return dict(sorted(Counter(x for x in v if x).items(),key=lambda x:(-x[1],x[0])))
def main():
 if len(TARGETS)!=13 or len(set(TARGETS))!=13:raise RuntimeError('Expected 13 unique targets')
 items=json.loads(FILES[0].read_text(encoding='utf8'));public=json.loads(FILES[1].read_text(encoding='utf8'))
 if items!=public or len(items)!=45851:raise RuntimeError('Unexpected starting state')
 before={x['id']:x for x in items};missing=[x for x in TARGETS if x not in before]
 if missing:raise RuntimeError(f'Missing targets: {missing}')
 if any(before[x].get('source')!='مكتبة القاضي محمد الأهدل القانونية والقضائية' for x in TARGETS):raise RuntimeError('Unexpected source')
 after=[x for x in items if x['id'] not in set(TARGETS)];afterby={x['id']:x for x in after}
 if len(after)!=45838 or any(x in afterby for x in TARGETS):raise RuntimeError('Unexpected deletion result')
 if any(afterby[k]!=v for k,v in before.items() if k not in set(TARGETS)):raise RuntimeError('Non-target record changed')
 stats=json.loads(STAT[0].read_text(encoding='utf8'));stats['total_items']=len(after)
 if 'total' in stats:stats['total']=len(after)
 stats['categories']=cnt(str(x.get('category','')) for x in after);stats['sources']=cnt(str(x.get('source','')) for x in after);stats['material_types']=cnt(str(x.get('material_type','')) for x in after);stats['file_types']=cnt(str(x.get('file_type','')) for x in after);stats['featured_count']=sum(bool(x.get('is_featured')) for x in after);stats['with_download_links']=sum(int(x.get('download_links_count') or 0)>0 for x in after)
 for p in FILES:dump(p,after)
 for p in STAT:dump(p,stats)
 h=HOOK.read_text(encoding='utf8');old='qadaa-yemen-cleanup-final-2026-10-04';new='qadaa-yemen-cleanup-complete-2026-10-04'
 if old not in h:raise RuntimeError('Cache token mismatch')
 HOOK.write_text(h.replace(old,new),encoding='utf8')
 result={'operation':'direct_yemen_residuals_exact_id_removal','executed_at_utc':datetime.now(timezone.utc).isoformat(),'before_total':len(items),'removed_total':len(TARGETS),'after_total':len(after),'removed_ids':TARGETS,'non_targets_unchanged':True,'cache_token':new,'items_sha256':sha(FILES[0]),'public_items_sha256':sha(FILES[1]),'stats_sha256':sha(STAT[0]),'public_stats_sha256':sha(STAT[1])};dump(OUT,result);print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
