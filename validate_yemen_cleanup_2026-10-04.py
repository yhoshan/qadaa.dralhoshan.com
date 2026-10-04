#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BACKUP=ROOT/'backups/yemen_cleanup_2026-10-04'
MANIFEST=ROOT/'yemen_cleanup_final_manifest_2026-10-04.json'
OUT=ROOT/'yemen_cleanup_2026-10-04_validation.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def counts(v):return dict(sorted(Counter(x for x in v if x).items(),key=lambda x:(-x[1],x[0])))
def main():
 before=json.loads((BACKUP/'items_root_before.json').read_text(encoding='utf8'))
 after=json.loads((ROOT/'items.json').read_text(encoding='utf8'));public=json.loads((ROOT/'client/public/items.json').read_text(encoding='utf8'))
 stats=json.loads((ROOT/'stats.json').read_text(encoding='utf8'));pubstats=json.loads((ROOT/'client/public/stats.json').read_text(encoding='utf8'))
 manifest=json.loads(MANIFEST.read_text(encoding='utf8'));targets=manifest['ids'];targetset=set(targets)
 before_by={x['id']:x for x in before};after_by={x['id']:x for x in after}
 assert len(before)==46494 and len(after)==45838 and len(targets)==656 and len(targetset)==656
 assert all(x in before_by for x in targets) and not any(x in after_by for x in targets)
 assert len(after_by)==len(after) and after==public and stats==pubstats
 assert all(after_by[k]==v for k,v in before_by.items() if k not in targetset), 'A non-target record changed'
 assert stats['total_items']==len(after)
 assert stats['categories']==counts(str(x.get('category','')) for x in after)
 assert stats['sources']==counts(str(x.get('source','')) for x in after)
 assert stats['material_types']==counts(str(x.get('material_type','')) for x in after)
 assert stats['file_types']==counts(str(x.get('file_type','')) for x in after)
 assert stats['featured_count']==sum(bool(x.get('is_featured')) for x in after)
 assert stats['with_download_links']==sum(int(x.get('download_links_count') or 0)>0 for x in after)
 assert sum(stats[k] for k in ('qadaa_count','nizam_count','mohama_count'))==len(after)
 direct_patterns=[r'الجمهورية اليمنية',r'الجمهورية العربية اليمنية',r'جمهورية اليمن الديمقراطية',r'القانون اليمني',r'القوانين اليمنية',r'الدستور اليمني',r'وزارة العدل اليمنية',r'المحكمة العليا اليمنية',r'النيابة العامة اليمنية',r'مجلس النواب اليمني',r'مجلس الشورى اليمني',r'جامعة صنعاء',r'جامعة عدن',r'\.ye(?:[/?#]|$)|gov\.ye|moj\.ye']
 direct_hits=[]
 for x in after:
  text=' | '.join(str(x.get(k,'') or '') for k in ('title','author','investigator','publisher','source','link_telegram','link_drive','link_direct'))
  if any(re.search(p,text,re.I) for p in direct_patterns):direct_hits.append(x['id'])
 assert not direct_hits, f'Remaining direct Yemen signals: {direct_hits}'
 source_hits=[x['source'] for x in after if re.search(r'اليمن|yemen|\.ye',str(x.get('source','')),re.I)]
 assert not source_hits, f'Remaining Yemen source labels: {source_hits}'
 hook=(ROOT/'client/src/hooks/useItems.ts').read_text(encoding='utf8');assert 'qadaa-yemen-cleanup-complete-2026-10-04' in hook
 report={'status':'passed','before_total':len(before),'targeted_yemen_records':len(targets),'removed_total':len(targets),'after_total':len(after),'all_target_ids_absent':True,'non_target_records_unchanged':True,'remaining_direct_yemen_signals':0,'remaining_yemen_source_labels':0,'ids_unique':True,'root_public_items_match':True,'root_public_stats_match':True,'hero_counts_total':sum(stats[k] for k in ('qadaa_count','nizam_count','mohama_count')),'cache_token':'qadaa-yemen-cleanup-complete-2026-10-04','items_sha256':sha(ROOT/'items.json'),'public_items_sha256':sha(ROOT/'client/public/items.json'),'stats_sha256':sha(ROOT/'stats.json'),'public_stats_sha256':sha(ROOT/'client/public/stats.json')}
 OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
