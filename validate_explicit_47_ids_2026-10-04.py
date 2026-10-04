#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BACKUP=ROOT/'backups/explicit_47_ids_2026-10-04'
REQUEST=Path('/home/ubuntu/upload/pasted_content.txt')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 targets=re.findall(r'`([^`]+)`',REQUEST.read_text(encoding='utf8'))
 before=json.loads((BACKUP/'items_root_before.json').read_text(encoding='utf8'))
 after=json.loads((ROOT/'items.json').read_text(encoding='utf8'))
 public=json.loads((ROOT/'client/public/items.json').read_text(encoding='utf8'))
 stats=json.loads((ROOT/'stats.json').read_text(encoding='utf8'))
 before_by={x['id']:x for x in before}; after_by={x['id']:x for x in after}
 assert len(targets)==47 and len(set(targets))==47
 assert len(before)==46541 and len(after)==46494 and len(before)-len(after)==47
 assert all(x in before_by for x in targets)
 assert not any(x in after_by for x in targets)
 retained=[x for x in before_by if x not in set(targets)]
 assert len(retained)==len(after)
 assert all(after_by[x]==before_by[x] for x in retained), 'Non-target record changed'
 assert after==public, 'Published copy mismatch'
 assert len(after_by)==len(after), 'Duplicate IDs remain'
 assert stats['total_items']==len(after)
 assert sum(stats[k] for k in ['qadaa_count','nizam_count','mohama_count'])==len(after)
 source_counts=Counter(x.get('source') for x in after)
 assert source_counts['مكتبة القاضي محمد الأهدل القانونية والقضائية']==25112
 assert source_counts['مكتبة القاضي صلاح سيف القانونية والقضائية']==1082
 assert stats['sources']==dict(sorted(Counter(str(x.get('source','')) for x in after if x.get('source')).items(),key=lambda t:(-t[1],t[0]))), 'Source stats mismatch'
 report={'status':'passed','before_total':len(before),'after_total':len(after),'target_count':len(targets),'targets_absent':True,'non_targets_unchanged':True,'ids_unique':True,'public_copy_matches':True,'ahdal_count':source_counts['مكتبة القاضي محمد الأهدل القانونية والقضائية'],'qadi_salah_count':source_counts['مكتبة القاضي صلاح سيف القانونية والقضائية'],'items_sha256':sha(ROOT/'items.json'),'public_items_sha256':sha(ROOT/'client/public/items.json'),'stats_sha256':sha(ROOT/'stats.json'),'public_stats_sha256':sha(ROOT/'client/public/stats.json')}
 out=ROOT/'explicit_47_ids_2026-10-04_validation.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
