#!/usr/bin/env python3
"""Guarded integration of the reviewed three-channel batch to the 20,001 threshold."""
from __future__ import annotations
import hashlib,json,re,shutil,unicodedata
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parent
TARGET_TOTAL=20001
BASELINE_TOTAL=19389

def norm(value:str)->str:
 value=unicodedata.normalize('NFC',value or '')
 value=re.sub(r'[\u064B-\u065F\u0670]','',value)
 value=value.translate(str.maketrans({'أ':'ا','إ':'ا','آ':'ا','ٱ':'ا','ة':'ه','ى':'ي'}))
 value=re.sub(r'[0-9٠-٩]{4}\s*(?:هـ|ه|م)?','',value)
 value=re.sub(r'\b(?:اصدار|إصدار|طبعة|نسخة|محدثة|المحدثة)\b','',value)
 return re.sub(r'[^\w\u0600-\u06FF]+','',value.lower())

def sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()

def build_stats(items:list[dict])->dict:
 return {
  'total_items':len(items),
  'categories':dict(sorted(Counter(x.get('category','') for x in items if x.get('category')).items())),
  'sources':dict(sorted(Counter(x.get('source','') for x in items if x.get('source')).items())),
  'material_types':dict(sorted(Counter(x.get('material_type','') for x in items if x.get('material_type')).items())),
  'file_types':dict(sorted(Counter(x.get('file_type','') for x in items if x.get('file_type')).items())),
  'featured_count':sum(bool(x.get('is_featured')) for x in items),
  'with_download_links':sum(int(x.get('download_links_count',0) or 0)>0 for x in items),
 }

def main():
 items_path=ROOT/'items.json'; public_path=ROOT/'client/public/items.json'
 stats_path=ROOT/'stats.json'; public_stats_path=ROOT/'client/public/stats.json'
 items=json.loads(items_path.read_text(encoding='utf-8'))
 public=json.loads(public_path.read_text(encoding='utf-8'))
 if not isinstance(items,list) or not isinstance(public,list):raise RuntimeError('Unexpected items JSON schema')
 if len(items)!=BASELINE_TOTAL or len(public)!=BASELINE_TOTAL:raise RuntimeError(f'Expected baseline {BASELINE_TOTAL}, got {len(items)}/{len(public)}')
 if sha(items_path)!=sha(public_path):raise RuntimeError('Primary and public item JSON differ before integration')
 additions=json.loads((ROOT/'three_channel_20001_final_selection.json').read_text(encoding='utf-8'))
 file_records=[x for x in additions if not x['id'].startswith('azizlawyer_post_')]
 post_records=[x for x in additions if x['id'].startswith('azizlawyer_post_')]
 if len(file_records)!=378 or len(post_records)!=234 or len(additions)!=612:raise RuntimeError(f'Unexpected selection sizes: {len(file_records)}, {len(post_records)}')
 ids=[x['id'] for x in additions]
 if len(ids)!=len(set(ids)):raise RuntimeError('Duplicate candidate IDs')
 if set(ids)&{x.get('id') for x in items}:raise RuntimeError('Candidate ID exists in current catalogue')
 existing_titles={norm(x.get('title','')) for x in items};candidate_titles=[norm(x.get('title','')) for x in additions]
 if any(not x for x in candidate_titles):raise RuntimeError('Empty candidate title')
 if len(candidate_titles)!=len(set(candidate_titles)):raise RuntimeError('Duplicate normalized title inside selected batch')
 if existing_titles & set(candidate_titles):raise RuntimeError('A candidate title duplicates current data')
 for x in additions:
  if not x.get('link_telegram','').startswith('https://t.me/'):raise RuntimeError(f"Invalid link: {x['id']}")
  x.pop('score',None);x.pop('text_preview',None)
 new_items=items+additions
 if len(new_items)!=TARGET_TOTAL:raise RuntimeError(f'Expected {TARGET_TOTAL}; got {len(new_items)}')
 # Rebuild every derived field except hero-card totals, which refresh_hero_stats.mjs owns.
 stats=build_stats(new_items)
 # Preserve the current UI metadata when available, but never stale calculated counters.
 old_stats=json.loads(stats_path.read_text(encoding='utf-8'))
 for key in ('qadaa_count','nizam_count','mohama_count'):
  if key in old_stats:stats[key]=old_stats[key]
 items_path.write_text(json.dumps(new_items,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 public_path.write_text(json.dumps(new_items,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 stats_path.write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 public_stats_path.write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 execution={'baseline_total':BASELINE_TOTAL,'target_total':TARGET_TOTAL,'added_total':len(additions),'file_records':len(file_records),'text_posts':len(post_records),'by_source':dict(Counter(x['source'] for x in additions)),'selection_file':'three_channel_20001_final_selection.json','added_ids':ids}
 (ROOT/'three_channel_20001_batch_execution.json').write_text(json.dumps(execution,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(execution,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
