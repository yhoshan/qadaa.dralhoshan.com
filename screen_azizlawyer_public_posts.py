#!/usr/bin/env python3
"""Read-only selection of high-confidence text-only legal reference posts."""
from __future__ import annotations
import csv,json,re,unicodedata
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'three_channel_batch_2026-10-03_screening'
EXPORT=Path('/home/ubuntu/upload/pasted_file_5iOQID_result.json')
SOURCE='المحامي عبدالعزيز المطوع'; HANDLE='azizlawyer'; PUBLISHER='قناة ثقافة قانونية — المحامي عبدالعزيز المطوع (@azizlawyer)'
LEGAL=re.compile(r'نظام|لائح|قانون|تشريع|تنظيم|قضاء|قضائ|محكم|تحكيم|وساط|محام|مرافع|دعوى|دعاو|إثبات|محاكم|قاضي|تنفيذ|إفلاس|ملكي|عقار|عقد|عقود|شرك|تجار|عمال|عمل|تمويل|مال[يةي]|أوراق تجارية|تعويض|توكيل|توقيف|ضبط|جناي|جريم|عقوب|مخدر|دية|نيابة|حضان|طلاق|نفقة|تركة|ورث|صك|تستر|مرور|مدفوعات|بريد|خبرة|خبير|سوابق|تسبيب|اعتراف|عدلي|توثيق|إيجار|اجارة|بيوع|حوالة|كفيل|ضمان|امتياز|تظلم|ترخيص|تأديبي|انضباط|مكافحة|سلوك مهني|قواعد|مبادئ|الحق|المحكمة',re.I)
TITLE_LEGAL=re.compile(r'نظام|لائح|قانون|تشريع|تنظيم|قضاء|قضائ|محكم|تحكيم|وساط|محام|مرافع|دعوى|دعاو|إثبات|محكم[ةه]|قاضي|تنفيذ|إفلاس|ملكي|عقار|عقد|عقود|شرك|تجار|عمل|تمويل|مال[يةي]|أوراق تجارية|تعويض|توكيل|توقيف|ضبط|جناي|جريم|عقوب|مخدر|دية|نيابة|حضان|طلاق|نفقة|تركة|ورث|صك|تستر|مرور|مدفوعات|بريد|خبرة|سوابق|تسبيب|اعتراف|عدلي|توثيق|إيجار|اجارة|بيوع|حوالة|كفيل|ضمان|امتياز|تظلم|ترخيص|تأديبي|انضباط|مكافحة|سلوك مهني|قواعد|مبادئ|الحق|قرار|تعميم|شاهد|يمين|تقادم|مخالفات|المحكمة',re.I)
EXCLUDE=re.compile(r'إعلان|دورة|تدريب|سجل الآن|خصم|واتساب|سناب|استبانة|وظيفة|فرصة وظيفية|شهادة حضور|اختبار|مقابلة|تهنئ|رمضان|دعاء|حديث|كتاب (?!القانون|المحام|القضاء|الأحكام|المذكرات)|أصول الفقه|مذهب|مناسك|زكاة|صيام|تفسير',re.I)
def text(m):
 v=m.get('text','');return ''.join(p.get('text','') if isinstance(p,dict) else str(p) for p in v) if isinstance(v,list) else str(v or '')
def clean(v):
 v=unicodedata.normalize('NFC',v or '')
 v=''.join(ch for ch in v if unicodedata.category(ch) not in {'Cf','So'})
 v=re.sub(r'[#*_`~]+','',v);v=re.sub(r'\s+',' ',v).strip(' -–—.،؛:')
 return v
def norm(v):
 v=clean(v);v=re.sub(r'[\u064B-\u065F\u0670]','',v);v=v.translate(str.maketrans({'أ':'ا','إ':'ا','آ':'ا','ٱ':'ا','ة':'ه','ى':'ي'}));return re.sub(r'[^\w\u0600-\u06FF]+','',v.lower())
def title_from(v):
 lines=[clean(x) for x in v.splitlines() if clean(x)]
 if not lines:return ''
 first=lines[0]
 # Use a meaningful first sentence as the display title; do not fabricate descriptions.
 first=re.split(r'(?<=[.!؟])\s+',first)[0]
 return first[:170].strip(' -–—.،؛:')
def category(v):
 if re.search(r'تحكيم|وساط|المحكم(?:ين)?\b',v):return 'التحكيم والوساطة'
 if re.search(r'محام|مرافع|دعوى|دعاو',v):return 'المحاماة والمرافعات'
 if re.search(r'أحوال|حضان|طلاق|نفقة|تركة|ورث|دية',v):return 'الأحوال الشخصية والتركات'
 if re.search(r'قضاء|قضائ|إثبات|محاكم|قاضي|نيابة|تنفيذ|سوابق|جناي|جريم|عقوب|ضبط|توقيف',v):return 'القضاء والإثبات'
 return 'الأنظمة والتشريعات'
def score(v,t):
 s=0
 s+=min(8,len(LEGAL.findall(v)))
 if re.search(r'نظام|لائح|قانون|حكم|قضاء|محكم|دعوى|دعوى|محكمة|مرافعة|تنفيذ|إثبات|قرار|تعميم',v):s+=4
 if 60<=len(v)<=4500:s+=2
 if 15<=len(t)<=170:s+=2
 if re.search(r'رابط|https?://|t\.me|youtube|snapchat',t,re.I):s-=8
 if EXCLUDE.search(v):s-=15
 return s
def main():
 data=json.loads(EXPORT.read_text(encoding='utf-8'))
 current=json.loads((ROOT/'items.json').read_text(encoding='utf-8'))
 existing={norm(str(x.get('title',''))) for x in current if x.get('title')}
 # Also eliminate titles already accepted as file candidates.
 files=json.loads((OUT/'candidates.json').read_text(encoding='utf-8'))
 existing|={norm(x['title']) for x in files}
 seen=set();rows=[];ex=[]
 for m in data['messages']:
  if m.get('file_name') or m.get('photo') or str(m.get('mime_type','')).startswith('video/'): continue
  v=text(m);t=title_from(v);k=norm(t);sc=score(v,t)
  base={'message_id':m.get('id'),'date':m.get('date',''),'title':t,'score':sc,'text_preview':clean(v)[:500]}
  if not t or len(t)<15 or not TITLE_LEGAL.search(t) or not LEGAL.search(v) or EXCLUDE.search(v) or sc<8:
   ex.append({**base,'reason':'لا يحقق معيار منشور قانوني نصي مستقل وعالي الثقة'});continue
  if k in existing or k in seen:
   ex.append({**base,'reason':'تطابق عنواني منضبط مع مادة قائمة أو مرشحة'});continue
  seen.add(k)
  rows.append({**base,'id':f"azizlawyer_post_{m['id']}",'author':'','investigator':'','publisher':PUBLISHER,'year':str(m.get('date',''))[:4] if m.get('date') else '','link_telegram':f"https://t.me/{HANDLE}/{m['id']}",'link_drive':'','link_direct':'','source':SOURCE,'category':category(v),'material_type':'بحث','file_type':'رابط','file_size':'','pages_count':'','is_featured':False,'download_links_count':1,'source_message_id':m['id'],'integration_note':'منشور قانوني نصي عام؛ عنوانه مقتبس من أول سطر في المصدر دون تنزيل مرفقات.'})
 rows.sort(key=lambda x:(-x['score'],x['message_id']))
 for name,items in [('public_post_candidates.json',rows),('public_post_excluded.json',ex)]:(OUT/name).write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 for name,items in [('public_post_candidates.csv',rows),('public_post_excluded.csv',ex)]:
  with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
   w=csv.DictWriter(f,fieldnames=sorted({k for r in items for k in r}));w.writeheader();w.writerows(items)
 print(json.dumps({'candidate_posts':len(rows),'excluded_posts':len(ex),'by_category':dict(Counter(x['category'] for x in rows)),'top_30':[{'id':x['id'],'score':x['score'],'title':x['title']} for x in rows[:30]]},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
