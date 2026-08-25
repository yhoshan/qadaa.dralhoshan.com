import { mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import path from 'node:path';
const root=process.cwd(),queue=JSON.parse(readFileSync(path.join(root,'remaining_telegram_critical_review_queue.json'),'utf8')).critical_queue,dir=path.join(root,'remaining_telegram_critical_review_chunks');rmSync(dir,{recursive:true,force:true});mkdirSync(dir,{recursive:true});
const records=queue.map((record,index)=>{const file=path.join(dir,`critical_${String(index+1).padStart(3,'0')}.json`);writeFileSync(file,`${JSON.stringify(record,null,2)}\n`);return {id:record.id,file};});writeFileSync(path.join(root,'remaining_telegram_critical_review_manifest.json'),`${JSON.stringify({count:records.length,records},null,2)}\n`);console.log(JSON.stringify(records,null,2));
