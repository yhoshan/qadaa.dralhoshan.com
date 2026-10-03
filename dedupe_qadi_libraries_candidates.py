#!/usr/bin/env python3
"""Conservatively remove token-set duplicates from the two pending library batches.
Does not modify items.json. Keeps current-catalogue records preferentially, then the
first candidate in stable source/post order. It never merges different numbered volumes.
"""
from __future__ import annotations
import json,re,unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path('/home/ubuntu/makanez-qadaa')
ITEMS=ROOT/'items.json'
AHDAL=ROOT/'qadi_ahdal_2026-10-03_candidates.json'
SALAH=ROOT/'qadi_salah_2026-10-03_candidates.json'
TASHEEL=ROOT/'tasheel_anzimah_2026-10-03_candidates.json'
OUT=ROOT/'qadi_libraries_2026-10-03_candidates_deduped.json'
EXCL=ROOT/'qadi_libraries_2026-10-03_duplicate_exclusions.json'
SUMMARY=ROOT/'qadi_libraries_2026-10-03_dedupe_summary.json'
DIAC=re.compile(r'[\u064B-\u065F\u0670\u06D6-\u06ED]')
STOP={'في','من','عن','على','الى','إلى','مع','بشأن','هذا','هذه','ذلك','تلك','لـ','الخاص','العامة','العام','القانون','نظام','النظام','قانون','شرح','كتاب','بحث','دراسة','حول','مبادئ','قواعد','المملكة','العربية','السعودية','اليمنية','اليمني','اليمن'}
def norm(v):
 v=unicodedata.normalize('NFKC',v or '');v=DIAC.sub('',v);v=v.translate(str.maketrans('أإآٱىةؤئ','اااايهوي'));v=re.sub(r'[^\w\s]',' ',v,flags=re.U);return re.sub(r'\s+',' ',v).strip().lower()
def signature(title):
 t=norm(title)
 tokens=re.findall(r'[\u0621-\u064A]+|\d+',t)
 # Retain numbers: volumes/issues/dates often distinguish actual records.
 tokens=[x for x in tokens if x not in STOP]
 return ' '.join(sorted(set(tokens)))
def main():
 items=json.loads(ITEMS.read_text(encoding='utf8'))
 ahdal=json.loads(AHDAL.read_text(encoding='utf8'))
 salah=json.loads(SALAH.read_text(encoding='utf8'))
 tasheel=json.loads(TASHEEL.read_text(encoding='utf8'))
 existing={}
 for x in items:
  sig=signature(str(x.get('title','')))
  if len(sig.split())>=2: existing.setdefault(sig,[]).append({'id':x.get('id'),'title':x.get('title'),'source':x.get('source')})
 kept=[];excluded=[];seen={}
 # Current catalogue always has priority; among new sources, retain the earlier
 # independently screened Tasheel record before equivalent library copies.
 for row in tasheel+ahdal+salah:
  sig=signature(row['title'])
  if len(sig.split())<2:
   kept.append(row);continue
  if sig in existing:
   excluded.append({'id':row['id'],'title':row['title'],'source':row['source'],'reason':'تطابق مجموعة الكلمات الجوهرية مع سجل قائم؛ منع تكرار محافظ.','matched_records':existing[sig]});continue
  if sig in seen:
   excluded.append({'id':row['id'],'title':row['title'],'source':row['source'],'reason':'تطابق مجموعة الكلمات الجوهرية مع مرشح سابق؛ أبقيت المرشح الأسبق فقط.','matched_records':[{'id':seen[sig]['id'],'title':seen[sig]['title'],'source':seen[sig]['source']}]});continue
  seen[sig]=row;kept.append(row)
 OUT.write_text(json.dumps(kept,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 EXCL.write_text(json.dumps(excluded,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 summary={'before':{'tasheel':len(tasheel),'ahdal':len(ahdal),'salah':len(salah),'total':len(tasheel)+len(ahdal)+len(salah)},'after_dedupe':len(kept),'excluded':len(excluded),'exclusions_by_reason':dict(Counter(x['reason'] for x in excluded)),'kept_by_source':dict(Counter(x['source'] for x in kept)),'checks':{'ids_unique':len(kept)==len({x['id'] for x in kept}),'no_political_title':not any(re.search(r'الحوث|انصار الله|أنصار الله|حزب الله|حماس|داعش|القاعدة|تنظيم الدولة|جبهة النصرة|غزة|فلسطين|إسرائيل|اسرائيل|الاحتلال',x['title'],re.I) for x in kept)}}
 SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
