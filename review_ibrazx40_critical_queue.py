import concurrent.futures as futures
import json
import time
from pathlib import Path
from openai import OpenAI

ROOT = Path('/home/ubuntu/makanez-qadaa')
QUEUE = json.loads((ROOT / 'ibrazx40_critical_review_queue.json').read_text(encoding='utf-8'))['items']
OUT = ROOT / 'ibrazx40_critical_reviews.json'
client = OpenAI()
SYSTEM = '''أنت محكّم نهائي شديد الدقة لمصدر قانون دولي. قيّم السجل هل يعالج القانون الدولي معالجة قانونية مباشرة أم أنه سياسة/علاقات دولية/أمن/استراتيجية/تاريخ/أيديولوجيا بلا إطار قانوني. 
لا تحذف بسبب أسماء دول أو جماعات أو كلمات الإرهاب أو فلسطين أو إيران أو منظمات أو دولة وحدها. أبقِ القانون الإنساني، حقوق الإنسان القانونية، الجرائم الدولية، الاحتلال، الإرهاب عندما يكون الإطار قانونياً. 
اجعل REMOVE فقط عندما تدل البيانات بوضوح على تحليل سياسي أو استراتيجي أو فكري أو تاريخي خارج القانون. REVIEW للغموض الحقيقي فقط. أخرج سبباً موجزاً محدداً بالعربية.'''
SCHEMA = {'type':'json_schema','json_schema':{'name':'critical_international_law_review','strict':True,'schema':{'type':'object','properties':{'decision':{'type':'string','enum':['KEEP','REMOVE','REVIEW']},'reason':{'type':'string'},'confidence':{'type':'integer','minimum':0,'maximum':100}},'required':['decision','reason','confidence'],'additionalProperties':False}}}

def one(item):
    record = item['record']
    payload = {key: record.get(key, '') for key in ['id','title','author','investigator','publisher','year','source','category','material_type','file_type','link_telegram','link_drive','link_direct','pages_count']}
    payload['initial_decision'] = item['initial']['decision']; payload['initial_reason'] = item['initial']['reason']; payload['risk_indicators'] = item['indicators']
    error = ''
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(model='gpt-5', messages=[{'role':'system','content':SYSTEM},{'role':'user','content':json.dumps(payload,ensure_ascii=False)}], response_format=SCHEMA, max_completion_tokens=500, extra_body={'reasoning': {'effort': 'medium'}})
            data = json.loads(resp.choices[0].message.content)
            return {'id':record['id'], 'title':record['title'], 'initial_decision':item['initial']['decision'], **data, 'error':''}
        except Exception as exc:
            error = str(exc); time.sleep(2*(attempt+1))
    return {'id':record['id'], 'title':record['title'], 'initial_decision':item['initial']['decision'], 'decision':'REVIEW', 'reason':'تعذر اكتمال التحكيم النقدي؛ يلزم مراجعة بشرية.', 'confidence':0, 'error':error}

with futures.ThreadPoolExecutor(max_workers=6) as pool: rows = list(pool.map(one, QUEUE))
rows.sort(key=lambda x:x['id'])
OUT.write_text(json.dumps({'total':len(rows),'reviews':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'total':len(rows), **{d:sum(r['decision']==d for r in rows) for d in ['KEEP','REMOVE','REVIEW']}, 'errors':sum(bool(r['error']) for r in rows)},ensure_ascii=False))
