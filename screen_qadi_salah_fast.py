#!/usr/bin/env python3
"""Deterministic conservative title screening for مكتبة القاضي صلاح سيف.
No catalogue changes; political materials and uncertain titles are excluded.
"""
from __future__ import annotations
import hashlib,json,re,unicodedata
from collections import Counter
from pathlib import Path
ROOT=Path('/home/ubuntu/makanez-qadaa')
EXPORT=Path('/home/ubuntu/upload/pasted_file_xuKUhg_result.json')
ITEMS=ROOT/'items.json'
OTHER=ROOT/'qadi_ahdal_2026-10-03_candidates.json'
RAW=ROOT/'qadi_salah_2026-10-03_raw_pdf_inventory.json'
CAND=ROOT/'qadi_salah_2026-10-03_candidates.json'
EXCL=ROOT/'qadi_salah_2026-10-03_excluded.json'
SUMMARY=ROOT/'qadi_salah_2026-10-03_precheck.json'
CONTROL=re.compile(r'[\u200e\u200f\u202a-\u202e\u2066-\u2069]')
DIAC=re.compile(r'[\u064B-\u065F\u0670\u06D6-\u06ED]')
POLITICAL=re.compile(r'الحوث|انصار الله|أنصار الله|حزب الله|حزب |الأحزاب|سياس(?:ة|ي)|انتخاب|برلمان|مجلس النواب|رئيس الجمهوري|ثورة|انقلاب|دبلوماس|المؤتمر الشعبي|البعث|الإخوان|الميليش|مليشيا|جماعة مسلحة|حرب|حماس|داعش|القاعدة|تنظيم الدولة|جبهة النصرة|غزة|فلسطين|إسرائيل|اسرائيل|الاحتلال',re.I)
LEGAL=re.compile(r'قانون|نظام|لائحة|تشريع|قضائ|محكم|حكم قضائي|حكم المحكمة|أحكام قضائية|مبادئ قضائية|دعوى|دعاوى|قاض|مرافعات|تنفيذ|إثبات|نيابة|تحقيق|جنائ|جريمة|عقوب|جرائم|محام|محاماة|عقد|عقود|التزام|مدني|تجاري|شركة|شركات|إفلاس|تحكيم|وساطة|إداري|دستور|ضريبة|جمارك|مصرف|تمويل|تأمين|ملكية فكرية|حقوق المؤلف|علامات تجارية|براءة اختراع|سجل تجاري|سجل عقاري|منافسات|مشتريات|استملاك|وقف شرعي|أحوال شخصية|طلاق|زواج|تركة|مواريث|وصية|طب شرعي|علم الاجرام|علم العقاب|قانوني|عدلي|قانونية|قضائية|اتفاقية|معاهدة|قواعد دولية|قانون دولي|مجلة الحقوق|مجلة القانون|سلطة قضائية|مهنة المحاماة|الوثائق|التوثيق',re.I)
NONLEGAL=re.compile(r'رواية|ديوان|شعر|قصة|قصص|السيرة الذاتية|مذكرات (?!قانون)|تفسير|آيات الاحكام|القرآن|الحديث|العقيدة|التوحيد|فقه (?!القضاء|المعاملات|الجنايات)|أصول الفقه|اللغة|النحو|البلاغة|التاريخ (?!القضائي)|جغرافيا|طب(?! شرعي)|هندسة|زراعة|كيمياء|فيزياء|رياضيات|طبخ|تربية|تعليم(?! العالي|القانوني)|إدارة (?!قضائية|قانونية)|اقتصاد(?!ي قانوني| وقانوني)|تنمية بشرية|تصوف|أدب',re.I)

def clean(v):
 v=unicodedata.normalize('NFKC',v or '');v=CONTROL.sub('',v);v=re.sub(r'\.pdf$','',v,flags=re.I);v=v.replace('_',' ');return re.sub(r'\s+',' ',v).strip(' .-_–—')
def norm(v):
 v=DIAC.sub('',clean(v)).translate(str.maketrans('أإآٱىةؤئ','اااايهوي'));return re.sub(r'\s+',' ',re.sub(r'[^\w\s]',' ',v,flags=re.U)).strip().lower()
def text_val(x):
 v=x.get('text','')
 if isinstance(v,str): return v
 if isinstance(v,list): return ' '.join(y if isinstance(y,str) else str(y.get('text','')) for y in v)
 return ''
def label(n): return f'{n/(1024*1024):.1f} MB' if n else ''
def classify(t):
 if re.search(r'مجلة|دورية',t): return 'الدراسات القانونية','مجلة'
 if re.search(r'أحكام|مبادئ|سوابق|نقض|تمييز|محكمة|قضائ',t): return 'القضاء والأحكام والإجراءات','أحكام'
 if re.search(r'شرح|تعليق|وجيز|مدخل|نظرية|دليل|ملخص|فقه القضاء',t): return 'الدراسات القانونية','شرح'
 if re.search(r'لائحة|قرار|تعميم',t): return 'الأنظمة والقانون العام','لائحة' if 'لائحة' in t else 'قرار'
 if re.search(r'قانون|نظام|تشريع',t):
  if re.search(r'جنائ|جريمة|عقوب|مخدر|سجن|إجرام',t): return 'القانون الجنائي','نظام'
  if re.search(r'تجاري|شركة|إفلاس|مصرف|تمويل|تأمين|ضريبة|جمارك|منافسات|مشتريات',t): return 'القانون التجاري والمالي','نظام'
  if re.search(r'مدني|عقد|التزام|عقار|إيجار|ملكية|استهلاك',t): return 'القانون المدني والعقاري','نظام'
  if re.search(r'دولي|اتفاقية|معاهدة',t): return 'القانون الدولي والمقارن','اتفاقية دولية' if re.search(r'اتفاقية|معاهدة',t) else 'نظام'
  if re.search(r'دستور|إداري|دولة|وظيف',t): return 'القانون الإداري والدستوري','نظام'
  if re.search(r'أحوال شخصية|تركة|وصية|زواج|طلاق|مواريث',t): return 'الأحوال الشخصية والتركات','نظام'
  return 'الأنظمة والقانون العام','نظام'
 if re.search(r'محام|مرافعة|مذكرة|صياغة|دفاع',t):return 'المحاماة والصياغة القانونية','دليل إجرائي'
 if re.search(r'تحكيم|وساطة',t):return 'القانون الدولي والمقارن','قواعد دولية'
 if re.search(r'رسالة|أطروحة|دراسة|بحث',t):return 'الدراسات القانونية','بحث'
 if re.search(r'ملكية فكرية|مؤلف|علامة تجارية|براءة',t):return 'الملكية الفكرية','مادة قانونية'
 return 'الدراسات القانونية','كتاب'
def main():
 data=json.loads(EXPORT.read_text(encoding='utf8'));items=json.loads(ITEMS.read_text(encoding='utf8'));other=json.loads(OTHER.read_text(encoding='utf8'))
 existing={norm(str(x.get('title',''))) for x in items+other if norm(str(x.get('title','')))}
 raw=[];last_text='';lastid=-999
 for m in data['messages']:
  txt=clean(text_val(m))
  if m.get('type')=='message' and txt and not m.get('file_name'): last_text,lastid=txt,int(m.get('id',-999))
  if m.get('type')!='message' or m.get('mime_type')!='application/pdf' or not m.get('file_name'):continue
  post=int(m['id']);title=clean(str(m['file_name']));ctx=txt or (last_text if post-lastid<=2 else '')
  raw.append({'post_id':post,'id':f'qadi_salah_{post}','title':title,'context':ctx[:600],'date':str(m.get('date','')),'file_name':m['file_name'],'file_size_bytes':m.get('file_size'),'telegram_url':f'https://t.me/estsharesalah/{post}'})
 assert len(raw)==5184
 RAW.write_text(json.dumps(raw,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 c=[];e=[];seen={}
 for r in raw:
  combined=f"{r['title']} {r['context']}";key=norm(r['title'])
  if len(re.sub(r'[^\u0621-\u064Aa-zA-Z]','',r['title']))<7: e.append({**r,'reason':'اسم غير وصفي أو رقمي.'});continue
  if POLITICAL.search(combined):e.append({**r,'reason':'استبعاد سياسي صريح وفق قرار المستخدم.'});continue
  if not LEGAL.search(combined):e.append({**r,'reason':'لا تظهر صلة قانونية أو قضائية كافية.'});continue
  if NONLEGAL.search(combined) and not LEGAL.search(r['title']):e.append({**r,'reason':'محتوى عام أو ديني/أدبي بلا صلة قانونية ظاهرة.'});continue
  if key in existing:e.append({**r,'reason':'عنوان مطابق بعد التطبيع لسجل قائم أو مرشح معتمد من مكتبة أخرى.'});continue
  if key in seen:e.append({**r,'reason':f'تكرار مطابق داخل المصدر؛ أبقيت {seen[key]} فقط.'});continue
  seen[key]=r['id'];cat,typ=classify(r['title'])
  c.append({'id':r['id'],'title':r['title'],'author':'مكتبة القاضي صلاح سيف','investigator':'','publisher':'','year':r['date'][:4],'link_telegram':r['telegram_url'],'link_drive':'','link_direct':'','source':'مكتبة القاضي صلاح سيف القانونية والقضائية','category':cat,'material_type':typ,'file_type':'PDF','file_size':label(r['file_size_bytes']),'pages_count':'','is_featured':False,'download_links_count':1})
 CAND.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf8');EXCL.write_text(json.dumps(e,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 s={'source_name':data.get('name'),'source_id':data.get('id'),'raw_pdf_records':len(raw),'accepted_candidates':len(c),'excluded_records':len(e),'excluded_by_reason':dict(Counter(x['reason'] for x in e)),'accepted_by_category':dict(Counter(x['category'] for x in c)),'accepted_by_material_type':dict(Counter(x['material_type'] for x in c)),'items_before_count':len(items),'items_before_sha256':hashlib.sha256(ITEMS.read_bytes()).hexdigest(),'candidate_ids_sha256':hashlib.sha256('\n'.join(x['id'] for x in c).encode()).hexdigest(),'checks':{'candidate_ids_unique':len(c)==len({x['id'] for x in c}),'no_normalized_title_overlap_with_existing_or_ahdal':not any(norm(x['title']) in existing for x in c)}}
 SUMMARY.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(s,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
