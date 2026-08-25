import concurrent.futures as futures
import json
import time
from pathlib import Path
from openai import OpenAI

ROOT = Path('/home/ubuntu/makanez-qadaa')
CANDIDATES = json.loads((ROOT / 'ibrazx40_merged_audit_reviews.json').read_text(encoding='utf-8'))['final_candidates']
client = OpenAI()
SYSTEM = '''أنت المحكّم النهائي لمكنز قانوني. احسم بدقة: KEEP للقانون الدولي الحقيقي؛ REMOVE للسياسة أو العلاقات الدولية أو الأمن والاستراتيجية أو التاريخ أو الأيديولوجيا من دون معالجة قانونية مباشرة؛ REVIEW فقط لغموض لا يحسم. 
المعيار: لا تُخرج موضوعاً قانونياً بسبب وجود كلمات دولة أو فلسطين أو إيران أو إرهاب أو أمن، ولا تُبقِ تحليلاً سياسياً لمجرد احتوائه على كلمة دولي. راجع العنوان والتصنيف وبيانات السجل وقراري الفحص السابقين. اذكر سبباً عربياً محدداً.'''
SCHEMA={'type':'json_schema','json_schema':{'name':'final_adjudication','strict':True,'schema':{'type':'object','properties':{'decision':{'type':'string','enum':['KEEP','REMOVE','REVIEW']},'reason':{'type':'string'},'confidence':{'type':'integer','minimum':0,'maximum':100}},'required':['decision','reason','confidence'],'additionalProperties':False}}}
def one(candidate):
    payload={'record':candidate['record'], 'initial':{'decision':candidate['merged']['decision'],'reason':candidate['merged']['reason']}, 'critical':candidate['merged']['critical_review'], 'provisional':{'decision':candidate['merged']['final_decision'],'reason':candidate['merged']['final_reason']}}
    error=''
    for attempt in range(3):
        try:
            res=client.chat.completions.create(model='gpt-5',messages=[{'role':'system','content':SYSTEM},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}],response_format=SCHEMA,max_completion_tokens=500,extra_body={'reasoning':{'effort':'high'}})
            data=json.loads(res.choices[0].message.content)
            return {'id':candidate['record']['id'],'title':candidate['record']['title'],**data,'error':''}
        except Exception as exc:
            error=str(exc);time.sleep(2*(attempt+1))
    return {'id':candidate['record']['id'],'title':candidate['record']['title'],'decision':candidate['merged']['final_decision'],'reason':candidate['merged']['final_reason'],'confidence':candidate['merged']['final_confidence'],'error':error}
with futures.ThreadPoolExecutor(max_workers=5) as pool: rows=list(pool.map(one,CANDIDATES))
rows.sort(key=lambda row:row['id'])
(ROOT/'ibrazx40_final_adjudications.json').write_text(json.dumps({'total':len(rows),'adjudications':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'total':len(rows),**{d:sum(row['decision']==d for row in rows) for d in ['KEEP','REMOVE','REVIEW']},'errors':sum(bool(row['error']) for row in rows)},ensure_ascii=False))
