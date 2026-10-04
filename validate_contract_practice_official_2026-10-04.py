#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
items=json.loads((ROOT/'items.json').read_text(encoding='utf-8'))
pitems=json.loads((ROOT/'client/public/items.json').read_text(encoding='utf-8'))
stats=json.loads((ROOT/'stats.json').read_text(encoding='utf-8'))
pstats=json.loads((ROOT/'client/public/stats.json').read_text(encoding='utf-8'))
assert items==pitems, 'اختلاف النسختين المنشورتين للمواد'
assert stats==pstats, 'اختلاف النسختين المنشورتين للإحصاءات'
assert len(items)==45830 and stats['total_items']==45830, (len(items),stats['total_items'])
ids=[x['id'] for x in items]
assert len(ids)==len(set(ids)), 'معرفات مكررة'
new=next(x for x in items if x['id']=='monshaat_mou_template_001')
assert new['title']=='نموذج مذكرة التفاهم'
assert new['link_direct']=='https://www.monshaat.gov.sa/ar/node/14322'
assert new['source']=='منشآت — الأدلة والأدوات'
it=next(x for x in items if x['id']=='rabab_library_1662')
assert it['link_direct'].startswith('https://etimad.sa/')
assert it['source']=='وزارة المالية السعودية — العقود والمشاريع'
assert it['link_telegram']=='https://t.me/c/1352319266/1662'
assert it['download_links_count']==2
report={'status':'passed','total_items':len(items),'new_id':new['id'],'upgraded_id':it['id'],'items_sha256':hashlib.sha256((ROOT/'items.json').read_bytes()).hexdigest(),'stats_sha256':hashlib.sha256((ROOT/'stats.json').read_bytes()).hexdigest()}
(ROOT/'contract_practice_official_2026-10-04_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
