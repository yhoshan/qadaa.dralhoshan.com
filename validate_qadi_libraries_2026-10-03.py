#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BACKUP=ROOT/'backups/qadi_libraries_2026-10-03'
CAND=ROOT/'qadi_libraries_2026-10-03_candidates_deduped.json'
EXEC=ROOT/'qadi_libraries_2026-10-03_execution.json'
OUT=ROOT/'qadi_libraries_2026-10-03_validation.json'
DIAC=re.compile(r'[\u064B-\u065F\u0670\u06D6-\u06ED]')
POL=re.compile(r'الحوث|انصار الله|أنصار الله|حزب الله|حماس|داعش|القاعدة|تنظيم الدولة|جبهة النصرة|غزة|فلسطين|إسرائيل|اسرائيل|الاحتلال',re.I)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(v):
 v=unicodedata.normalize('NFKC',v or '');v=DIAC.sub('',v);v=v.translate(str.maketrans('أإآٱىةؤئ','اااايهوي'));return re.sub(r'\s+',' ',re.sub(r'[^\w\s]',' ',v,flags=re.U)).strip().lower()
def countmap(rows,key):return dict(sorted(Counter(str(x.get(key) or '') for x in rows if x.get(key)).items(),key=lambda t:(-t[1],t[0])))
def main():
 before=json.loads((BACKUP/'items_before.json').read_text(encoding='utf8'));after=json.loads((ROOT/'items.json').read_text(encoding='utf8'));public=json.loads((ROOT/'client/public/items.json').read_text(encoding='utf8'));candidates=json.loads(CAND.read_text(encoding='utf8'));stats=json.loads((ROOT/'stats.json').read_text(encoding='utf8'));pstats=json.loads((ROOT/'client/public/stats.json').read_text(encoding='utf8'));exe=json.loads(EXEC.read_text(encoding='utf8'))
 before_by={x['id']:x for x in before};after_by={x['id']:x for x in after};cids={x['id'] for x in candidates};added=[x for x in after if x['id'] in cids]
 assert len(before)==20080 and len(after)==46541 and len(candidates)==26461 and len(added)==26461
 assert len(after_by)==len(after) and len(cids)==len(candidates)
 assert not(cids & set(before_by))
 assert set(after_by)-set(before_by)==cids
 assert all(after_by[k]==v for k,v in before_by.items())
 assert sha(ROOT/'items.json')==sha(ROOT/'client/public/items.json')
 assert sha(ROOT/'stats.json')==sha(ROOT/'client/public/stats.json')
 assert stats['total_items']==len(after)
 assert stats['categories']==countmap(after,'category')
 assert stats['sources']==countmap(after,'source')
 assert stats['material_types']==countmap(after,'material_type')
 assert stats['file_types']==countmap(after,'file_type')
 assert stats['featured_count']==sum(bool(x.get('is_featured')) for x in after)
 assert stats['with_download_links']==sum(int(x.get('download_links_count') or 0)>0 for x in after)
 assert not any(POL.search(x['title']) for x in added)
 assert all(x.get('link_telegram','').startswith('https://t.me/') and x.get('download_links_count')==1 for x in added)
 candidate_norms=[norm(x['title']) for x in candidates];existing_norms={norm(x['title']) for x in before};assert len(candidate_norms)==len(set(candidate_norms));assert not(set(candidate_norms)&existing_norms)
 hero={k:stats[k] for k in ('qadaa_count','nizam_count','mohama_count')};assert sum(hero.values())==len(after)
 assert exe['after_total']==len(after) and exe['items_sha256']==sha(ROOT/'items.json')
 hook=(ROOT/'client/src/hooks/useItems.ts').read_text(encoding='utf8');assert 'qadaa-qadi-libraries-2026-10-03' in hook
 result={'status':'passed','before_total':len(before),'candidate_total':len(candidates),'after_total':len(after),'added_by_source':dict(Counter(x['source'] for x in added)),'hero_counts':hero,'items_hash':sha(ROOT/'items.json'),'stats_hash':sha(ROOT/'stats.json'),'main_public_items_match':True,'main_public_stats_match':True,'ids_unique':True,'all_preexisting_records_unchanged':True,'new_titles_unique_and_not_preexisting':True,'political_titles_in_new_batch':0,'public_telegram_links_in_new_batch':len(added),'cache_token':'qadaa-qadi-libraries-2026-10-03','stats_rebuilt':True}
 OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
