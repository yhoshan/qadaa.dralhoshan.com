#!/usr/bin/env python3
"""Read-only inventory for the Hero's professional-law-practice counter."""
from __future__ import annotations
import json,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ITEMS=ROOT/'items.json'
OUT=ROOT/'mohama_practice_reclassification_2026-10-04_candidates.json'
SUMMARY=ROOT/'mohama_practice_reclassification_2026-10-04_summary.json'
# Categories whose normal use is directly tied to client advice, drafting, disputes,
# commercial practice, labour, family, and property legal work.
PRACTICE_CATEGORY=re.compile(r'(القانون المدني|العقاري|القانون التجاري|المالي|الأحوال الشخصية|الأسرة|المعاملات|التزامات|العقود|الشركات|الحوكمة|الإفلاس|العمالي|قانون العمل|أنظمة العمل|الملكية الفكرية|التأمين|المنافسات|القانون الإداري|قانون إداري|القانون الدستوري|قانون دستوري|الضرائب|الزكاة|الجمارك|الأوراق التجارية)',re.U)
# Directly professional titles even when the imported category is too generic.
PRACTICE_TITLE=re.compile(r'(صحيفة\s*(دعوى|استئناف|اعتراض)|لائحة\s*(دعوى|اعتراض)|مذكرة\s*(جواب|دفاع|قانونية|اعتراض)|صياغة\s*(العقود|عقد|قانونية)|نموذج\s*(عقد|دعوى|مذكرة|لائحة|وكالة)|أتعاب\s*المحام|مسؤولية\s*المحام|مهنة\s*المحام|وكالة\s*(شرعية|قانونية)|عقد\s*(تجاري|عمل|ايجار|إيجار|مقاولة|وكالة)|تصفية\s*الشركات|حوكمة\s*الشركات|إفلاس|تنفيذ\s*(الأحكام|السندات|العقود)|الملكية\s*الفكرية|علامة\s*تجارية|براءة\s*اختراع|منافسات\s*(ومشتريات|حكومية)|تأمين\s*(ضد|تعاوني|مسؤولية)|ضريبة|جمرك|زكاة)',re.U)
# A title explicitly about lawyers, arbitration, or mediation is professional practice.
PRACTICE_EXPLICIT_TITLE=re.compile(r'(محام|تحكيم|وساط)',re.U)
BASE_MOHAMA=re.compile(r'(محام|تحكيم|وساط)',re.U)
BASE_QADAA=re.compile(r'(قضاء|قضائي|محكم|مرافع|إثبات|جنا|جزائي|حسبة|مظالم|أحكام|إجراء.*قضائي|قرار.*قضائي)',re.U)

def base_group(category:str)->str:
    if BASE_MOHAMA.search(category): return 'mohama'
    if BASE_QADAA.search(category): return 'qadaa'
    return 'nizam'

def reason(item:dict)->str|None:
    category=str(item.get('category',''))
    title=str(item.get('title',''))
    # Only migrate records that belonged to the previous systems counter.
    if base_group(category)!='nizam': return None
    if PRACTICE_CATEGORY.search(category): return 'تصنيف موضوعي للممارسة القانونية'
    if PRACTICE_TITLE.search(title): return 'عنوان عملي مباشر للممارسة القانونية'
    if PRACTICE_EXPLICIT_TITLE.search(title): return 'عنوان صريح في المحاماة أو التحكيم أو الوساطة'
    return None

def main():
    items=json.loads(ITEMS.read_text(encoding='utf8'))
    rows=[]
    for x in items:
        why=reason(x)
        if why:
            rows.append({'id':x['id'],'title':x['title'],'source':x['source'],'category':x['category'],'material_type':x['material_type'],'reason':why})
    assert len(rows)==6571 and len({x['id'] for x in rows})==6571
    summary={'catalogue_total':len(items),'base_mohama_count':sum(base_group(str(x.get('category','')))=='mohama' for x in items),'base_qadaa_count':sum(base_group(str(x.get('category','')))=='qadaa' for x in items),'base_nizam_count':sum(base_group(str(x.get('category','')))=='nizam' for x in items),'migrated_from_base_nizam':len(rows),'new_mohama_count':1820+len(rows),'new_nizam_count':29856-len(rows),'qadaa_unchanged':14162,'by_reason':dict(Counter(x['reason'] for x in rows)),'by_category':dict(Counter(x['category'] for x in rows))}
    OUT.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    SUMMARY.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
