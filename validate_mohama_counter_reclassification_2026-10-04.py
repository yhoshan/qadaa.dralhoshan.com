#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BACKUP=ROOT/'backups/mohama_counter_reclassification_2026-10-04'
CANDIDATES=ROOT/'mohama_practice_reclassification_2026-10-04_candidates.json'
SUMMARY=ROOT/'mohama_practice_reclassification_2026-10-04_summary.json'
OUT=ROOT/'mohama_counter_reclassification_2026-10-04_validation.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 before_items=(BACKUP/'items_root_before.json').read_bytes();after_items=(ROOT/'items.json').read_bytes();before_public=(BACKUP/'items_public_before.json').read_bytes();after_public=(ROOT/'client/public/items.json').read_bytes()
 assert before_items==after_items and before_public==after_public and after_items==after_public, 'Item data changed unexpectedly'
 before_stats=json.loads((BACKUP/'stats_root_before.json').read_text(encoding='utf8'));after_stats=json.loads((ROOT/'stats.json').read_text(encoding='utf8'));public_stats=json.loads((ROOT/'client/public/stats.json').read_text(encoding='utf8'))
 assert after_stats==public_stats, 'Root/public stats mismatch'
 changed=[k for k in sorted(set(before_stats)|set(after_stats)) if before_stats.get(k)!=after_stats.get(k)]
 assert changed==['mohama_count','nizam_count'], f'Unexpected stats modifications: {changed}'
 assert before_stats['qadaa_count']==after_stats['qadaa_count']==14162
 assert before_stats['nizam_count']==29856 and after_stats['nizam_count']==23285
 assert before_stats['mohama_count']==1820 and after_stats['mohama_count']==8391
 assert after_stats['total_items']==45838 and sum(after_stats[x] for x in ('qadaa_count','nizam_count','mohama_count'))==45838
 candidates=json.loads(CANDIDATES.read_text(encoding='utf8'));summary=json.loads(SUMMARY.read_text(encoding='utf8'))
 assert len(candidates)==6571 and len({x['id'] for x in candidates})==6571
 assert summary['migrated_from_base_nizam']==6571 and summary['new_mohama_count']==8391 and summary['new_nizam_count']==23285
 current_ids={x['id'] for x in json.loads(after_items)}
 assert {x['id'] for x in candidates}.issubset(current_ids)
 hook=(ROOT/'client/src/hooks/useItems.ts').read_text(encoding='utf8')
 assert 'qadaa-mohama-professional-reclassification-2026-10-04' in hook
 report={'status':'passed','total_items':45838,'qadaa_before_after':[14162,14162],'nizam_before_after':[29856,23285],'mohama_before_after':[1820,8391],'migrated_from_nizam':6571,'items_unchanged':True,'only_expected_stats_changed':True,'root_public_items_match':True,'root_public_stats_match':True,'candidate_ids_unique':True,'cache_token':'qadaa-mohama-professional-reclassification-2026-10-04','items_sha256':sha(ROOT/'items.json'),'stats_sha256':sha(ROOT/'stats.json')}
 OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
