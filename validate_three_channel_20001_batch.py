#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BACKUP=ROOT/'backups/three_channel_20001_2026-10-03'
EXEC=ROOT/'three_channel_20001_batch_execution.json'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):
 import unicodedata
 s=unicodedata.normalize('NFC',s or '')
 s=re.sub(r'[\u064B-\u065F\u0670]','',s)
 s=s.translate(str.maketrans({'أ':'ا','إ':'ا','آ':'ا','ٱ':'ا','ة':'ه','ى':'ي'}))
 return re.sub(r'[^\w\u0600-\u06FF]+','',s.lower())
def calculated(items):
 return {'total_items':len(items),'categories':dict(sorted(Counter(x.get('category','') for x in items if x.get('category')).items())),'sources':dict(sorted(Counter(x.get('source','') for x in items if x.get('source')).items())),'material_types':dict(sorted(Counter(x.get('material_type','') for x in items if x.get('material_type')).items())),'file_types':dict(sorted(Counter(x.get('file_type','') for x in items if x.get('file_type')).items())),'featured_count':sum(bool(x.get('is_featured')) for x in items),'with_download_links':sum(int(x.get('download_links_count',0) or 0)>0 for x in items)}
def main():
 before=json.loads((BACKUP/'items_root_before.json').read_text(encoding='utf-8'))
 items=json.loads((ROOT/'items.json').read_text(encoding='utf-8'))
 public=json.loads((ROOT/'client/public/items.json').read_text(encoding='utf-8'))
 stats=json.loads((ROOT/'stats.json').read_text(encoding='utf-8'))
 public_stats=json.loads((ROOT/'client/public/stats.json').read_text(encoding='utf-8'))
 execution=json.loads(EXEC.read_text(encoding='utf-8'))
 assert len(before)==19389, len(before)
 assert len(items)==len(public)==20001
 assert sha(ROOT/'items.json')==sha(ROOT/'client/public/items.json')
 assert sha(ROOT/'stats.json')==sha(ROOT/'client/public/stats.json')
 ids=[x.get('id') for x in items]
 assert len(ids)==len(set(ids)) and all(ids)
 before_by_id={x['id']:x for x in before}
 after_by_id={x['id']:x for x in items}
 assert set(before_by_id)<=set(after_by_id)
 unchanged=all(before_by_id[i]==after_by_id[i] for i in before_by_id)
 assert unchanged
 added=set(execution['added_ids'])
 assert len(added)==612 and added==set(after_by_id)-set(before_by_id)
 selected=[after_by_id[x] for x in added]
 assert Counter(x['source'] for x in selected)==Counter({'المحامي الفقيه':19,'المحامي محمّد الشكرة':30,'المحامي عبدالعزيز المطوع':563})
 assert all(x['link_telegram'].startswith('https://t.me/') and int(x.get('download_links_count',0))==1 for x in selected)
 nt=[norm(x['title']) for x in selected]
 assert len(nt)==len(set(nt)) and not (set(nt)&{norm(x['title']) for x in before})
 expected=calculated(items)
 for k,v in expected.items():assert stats.get(k)==v,(k,stats.get(k),v)
 assert stats==public_stats
 hero=sum(stats[k] for k in ('qadaa_count','nizam_count','mohama_count'))
 assert hero==20001,hero
 report={'status':'passed','before_total':len(before),'after_total':len(items),'added_total':len(selected),'unchanged_preexisting_records':len(before),'duplicate_ids':len(ids)-len(set(ids)),'items_sha256':sha(ROOT/'items.json'),'stats_sha256':sha(ROOT/'stats.json'),'hero_counts':{k:stats[k] for k in ('qadaa_count','nizam_count','mohama_count')},'by_new_source':dict(Counter(x['source'] for x in selected)),'json_primary_public_match':True,'statistics_match_recalculation':True}
 (ROOT/'three_channel_20001_batch_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
