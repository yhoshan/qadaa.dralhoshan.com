import concurrent.futures as futures
import json
import time
from pathlib import Path
from openai import OpenAI

ROOT=Path('/home/ubuntu/makanez-qadaa')
GROUPS=json.loads((ROOT/'ibrazx40_duplicate_candidates.json').read_text(encoding='utf-8'))['groups']
client=OpenAI()
SYSTEM='''أنت محكم تكرار بيانات صارم. افحص مجموعة من سجلات مصدر واحد. صنفها DUPLICATE فقط إذا كانت الوثيقة نفسها أو نسخة موثقة متطابقة فعلاً؛ RELATED إذا كان العنوان مشابهاً لكن العملين مختلفين؛ UNCERTAIN عند غياب قرينة كافية. لا تعتبر الأجزاء أو الإصدارات المختلفة أو دراستين في موضوع واحد تكراراً. عند DUPLICATE اختر معرف نسخة مرجعية موجوداً واقترح بقية المعرفات زائدة، مع سبب محدد. لا تقترح حذفاً فعلياً.'''
SCHEMA={'type':'json_schema','json_schema':{'name':'duplicate_adjudication','strict':True,'schema':{'type':'object','properties':{'verdict':{'type':'string','enum':['DUPLICATE','RELATED','UNCERTAIN']},'keeper_id':{'type':'string'},'redundant_ids':{'type':'array','items':{'type':'string'}},'reason':{'type':'string'}},'required':['verdict','keeper_id','redundant_ids','reason'],'additionalProperties':False}}}
def one(group):
    error=''
    for attempt in range(3):
        try:
            resp=client.chat.completions.create(model='gpt-5-mini',messages=[{'role':'system','content':SYSTEM},{'role':'user','content':json.dumps(group,ensure_ascii=False)}],response_format=SCHEMA,max_completion_tokens=450)
            data=json.loads(resp.choices[0].message.content)
            valid={r['id'] for r in group['records']}
            if data['keeper_id'] not in valid or not set(data['redundant_ids']).issubset(valid-{data['keeper_id']}): raise ValueError('مخرجات معرفات غير مطابقة للمجموعة')
            if data['verdict']!='DUPLICATE': data['redundant_ids']=[]; data['keeper_id']=''
            return {'group_id':group['group_id'],**data,'error':''}
        except Exception as exc: error=str(exc); time.sleep(1.5*(attempt+1))
    return {'group_id':group['group_id'],'verdict':'UNCERTAIN','keeper_id':'','redundant_ids':[],'reason':'تعذر حسم التكرار آلياً؛ لا توصية حذف.','error':error}
with futures.ThreadPoolExecutor(max_workers=6) as pool: rows=list(pool.map(one,GROUPS))
rows.sort(key=lambda x:x['group_id'])
(ROOT/'ibrazx40_duplicate_adjudications.json').write_text(json.dumps({'total':len(rows),'adjudications':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'total':len(rows),**{v:sum(x['verdict']==v for x in rows) for v in ['DUPLICATE','RELATED','UNCERTAIN']},'errors':sum(bool(x['error']) for x in rows)},ensure_ascii=False))
