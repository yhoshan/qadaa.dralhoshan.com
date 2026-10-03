#!/usr/bin/env python3
"""Conservatively screen three public Telegram exports for legal reference records.
Titles and opening links only; no attachments are downloaded.
"""
from __future__ import annotations
import csv, json, re, unicodedata
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'three_channel_batch_2026-10-03_screening'
SOURCES=[
 {'file':'/home/ubuntu/upload/pasted_file_roJR9N_result.json','key':'almuhame_alfaqih','source':'المحامي الفقيه','handle':'almuhamealfaqih','publisher':'قناة المحامي الفقيه (@almuhamealfaqih)'},
 {'file':'/home/ubuntu/upload/pasted_file_OJCxMk_result.json','key':'mohammed_alshakrah','source':'المحامي محمّد الشكرة','handle':'Lawy2r','publisher':'قناة المحامي محمّد الشكرة (@Lawy2r)'},
 {'file':'/home/ubuntu/upload/pasted_file_5iOQID_result.json','key':'abdulaziz_almutawa','source':'المحامي عبدالعزيز المطوع','handle':'azizlawyer','publisher':'قناة ثقافة قانونية — المحامي عبدالعزيز المطوع (@azizlawyer)'},
]
LEGAL=re.compile(r'''نظام|لائح|قانون|تشريع|تنظيم|قضاء|قضائ|محكم|تحكيم|وساط|محام|مرافع|دعوى|دعاو|إثبات|محاكم|قاضي|تنفيذ|إفلاس|ملكي|عقار|عقد|عقود|شرك|تجار|عمال|عمل|تمويل|مال[يةي]|أوراق تجارية|تعويض|توكيل|توقيف|ضبط|جناي|جريم|عقوب|مخدر|دية|حدود|نيابة|حضان|طلاق|نفقة|تركة|ورث|أحوال شخصية|صك|تستر|مرور|مدفوعات|بريد|خبرة|خبير|سوابق|معايير|تسبيب|اعتراف|عدلي|توثيق|إيجار|إجارة|بيوع|حوالة|كفيل|ضمان|امتياز|تظلم|ترخيص|تأديبي|انضباط|مكافحة|سلوك مهني|مؤسسات العدلية|حقوق كبار السن|الدعوى الكيدية|قواعد الأتعاب|قضايا الخدمات الطبية|قواعد قانونية|صياغة قانونية|قانوني|legal|procedural|arbitration|settlement|ssac|code of ethics''',re.I|re.X)
EXCLUDE=re.compile(r'''رمضان|صيام|زكاة|مناسك|تفسير|سورة|أذكار|دعاء|من يدعوني|مدارج السالكين|الروض المربع|عقيدة|حديث|كتاب الأدعية|الملف الرمضاني|عرض مقرر|حاشية على الروض|مكتبة نفع القضائية|دبلومات المعهد|الشهادات المهنية|لمحات من العمل|total events|animation|خرائط ذهنية للروض|موسوعة القواعد الفقهية|أصول الفقه|مصادر فقهية|فقه الأسرة|فقه المعاملات|مقرر فقه|المعيار الشرعي للوقف|تفسير|المختصر في التفسير|كُتُب الأدعية|تجميع أسئلة مقابلة|اختبار النيابة النفسي|شهادات حضور|فرص وظيفية|قدرات الجامعيين|مذكرة الفقه$''',re.I|re.X)
GENERIC=re.compile(r'''^(?:pdf|ttmm|ahwaal|mshki\d*|sticker|animation|img[ _\d.-]*|\d+(?:[-_ ]\d+)*(?:\s*\(\d+\))?|__\d+|bf[0-9a-f-]+|الملف الجديد|المذكرة الإيضاحية|المقرر والمستقر|جميع الفوائد|الوعد|مذكرات النسخة النهائية|حماية المسافرين|مشكلات أول المعاملات|ملف)$''',re.I|re.X)

def msgtext(m):
 v=m.get('text','')
 return ''.join(p.get('text','') if isinstance(p,dict) else str(p) for p in v) if isinstance(v,list) else str(v or '')
def clean(s):
 s=unicodedata.normalize('NFC',s or '')
 s=''.join(ch for ch in s if unicodedata.category(ch) not in {'Cf','So'})
 s=re.sub(r'\.(?:pdf|docx?|mp4|mov|webp)$','',s,flags=re.I)
 s=s.replace('_',' ').replace('ـ',' ')
 s=re.sub(r'\s+',' ',s).strip(' -–—.،؛:()[]{}')
 return s
def norm(s):
 s=clean(s)
 s=re.sub(r'\(?\s*نسخة\s+(?:للطباعة|علي\s+\S+|[\w\s]+)?\)?','',s,flags=re.I)
 s=re.sub(r'\b(?:v\d+|ط\d+|الإصدار\s+\w+|النسخة\s+\w+|لعام\s+\d+هـ?|\d{4}هـ?)\b','',s,flags=re.I)
 s=unicodedata.normalize('NFC',s)
 s=re.sub(r'[\u064B-\u065F\u0670]','',s)
 s=s.translate(str.maketrans({'أ':'ا','إ':'ا','آ':'ا','ٱ':'ا','ة':'ه','ى':'ي'}))
 return re.sub(r'[^\w\u0600-\u06FF]+','',s.lower())
def pretty_size(v):
 try: n=int(v or 0)
 except: return ''
 return f'{n/1048576:.1f} MB' if n>=1048576 else f'{n/1024:.1f} KB' if n else ''
def category(t):
 if re.search(r'تحكيم|وساط|محكم|arbitration|settlement|ssac',t,re.I): return 'التحكيم والوساطة'
 if re.search(r'محام|مرافع|لائحة اعتراضية|دعوى|دعاو',t): return 'المحاماة والمرافعات'
 if re.search(r'أحوال|حضان|طلاق|نفقة|تركة|ورث|مواريث|فرائض|وقف|دية',t): return 'الأحوال الشخصية والتركات'
 if re.search(r'قضاء|قضائ|إثبات|محاكم|قاضي|نيابة|تنفيذ|سوابق|جناي|جريم|عقوب|ضبط|توقيف',t): return 'القضاء والإثبات'
 return 'الأنظمة والتشريعات'
def material(t):
 if re.search(r'شرح|تسهيل|تبسيط|تلخيص|تفنيد',t): return 'شرح'
 if re.search(r'بحث|دراسة|ورقة|ندوة|تعليق|تسبيبات',t): return 'بحث'
 if re.search(r'دليل|مرشد|فهرس|مصطلح|حقيبة|قائمة',t): return 'دليل'
 if re.search(r'نظام|لائحة|قانون|قواعد|تعليمات|قرار|procedural|code',t,re.I): return 'نظام'
 return 'كتاب'
def override(source,m,title):
 # File names that are technical but supplied caption names an explicit legal resource.
 if source['key']=='almuhame_alfaqih' and m.get('id')==1119: return 'لائحة عمل أمين سر لجنة التحكيم'
 if source['key']=='almuhame_alfaqih' and m.get('id')==1301: return 'الضوابط اللغوية للصياغة القانونية'
 return title

def main():
 OUT.mkdir(exist_ok=True)
 current=json.loads((ROOT/'items.json').read_text(encoding='utf-8'))
 existing={norm(str(x.get('title',''))) for x in current if x.get('title')}
 candidates=[]; duplicates=[]; excluded=[]; seen=set()
 source_stats={}
 for source in SOURCES:
  data=json.loads(Path(source['file']).read_text(encoding='utf-8'))
  stats=Counter()
  for m in data.get('messages',[]):
   filename=m.get('file_name'); mime=str(m.get('mime_type',''))
   if not filename or mime.startswith('video/') or mime.startswith('image/'):
    continue
   title=override(source,m,clean(str(filename)))
   text=msgtext(m); key=norm(title)
   base={'source':source['source'],'channel_handle':source['handle'],'message_id':m.get('id'),'date':m.get('date',''),'file_name':filename,'mime_type':mime,'file_size':m.get('file_size',0),'title':title}
   if not key or GENERIC.fullmatch(title):
    excluded.append({**base,'reason':'عنوان تقني أو عام لا يعرّف مادة قانونية بوضوح'});stats['excluded']+=1;continue
   if EXCLUDE.search(title):
    excluded.append({**base,'reason':'فقه عام أو مادة تدريبية/وعظية لا تدخل في منهج المكنز'});stats['excluded']+=1;continue
   if not LEGAL.search(title+' '+text):
    excluded.append({**base,'reason':'لا توجد دلالة قانونية أو قضائية كافية في العنوان أو وصف الرسالة'});stats['excluded']+=1;continue
   if key in existing:
    duplicates.append({**base,'reason':'تطابق عنواني منضبط مع سجل قائم في المكنز'});stats['duplicates']+=1;continue
   if key in seen:
    duplicates.append({**base,'reason':'تطابق عنواني منضبط داخل الدفعة الجديدة'});stats['duplicates']+=1;continue
   seen.add(key); stats['candidates']+=1
   candidates.append({'id':f"{source['key']}_{m['id']}",'title':title,'author':'','investigator':'','publisher':source['publisher'],'year':str(m.get('date',''))[:4] if m.get('date') else '','link_telegram':f"https://t.me/{source['handle']}/{m['id']}",'link_drive':'','link_direct':'','source':source['source'],'category':category(title),'material_type':material(title),'file_type':'Word' if 'wordprocessingml' in mime else 'PDF','file_size':pretty_size(m.get('file_size')),'pages_count':'','is_featured':False,'download_links_count':1,'source_message_id':m['id'],'integration_note':'عنوان ورابط رسالة عامة فقط؛ لم يُحمّل الملف.'})
  source_stats[source['source']]=dict(stats)
 result={'generated_at':'2026-10-03','sources':[{'name':s['source'],'handle':s['handle'],'channel_id':json.loads(Path(s['file']).read_text(encoding='utf-8')).get('id')} for s in SOURCES],'candidate_count':len(candidates),'duplicates_count':len(duplicates),'excluded_count':len(excluded),'source_stats':source_stats,'by_category':dict(sorted(Counter(x['category'] for x in candidates).items())),'by_material_type':dict(sorted(Counter(x['material_type'] for x in candidates).items())),'candidates':candidates,'duplicates':duplicates,'excluded_records':excluded}
 (OUT/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (OUT/'candidates.json').write_text(json.dumps(candidates,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 for name,rows in [('candidates.csv',candidates),('duplicates.csv',duplicates),('excluded.csv',excluded)]:
  fields=sorted({k for row in rows for k in row})
  with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
   w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 print(json.dumps({k:result[k] for k in ['candidate_count','duplicates_count','excluded_count','source_stats','by_category','by_material_type']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
