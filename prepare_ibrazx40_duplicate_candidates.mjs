import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
const root = process.cwd();
const records = JSON.parse(readFileSync(path.join(root, 'ibrazx40_source_audit_records.json'), 'utf8')).records;
const norm = (text) => String(text ?? '').toLowerCase().replace(/\.pdf$/i, '').replace(/[أإآا]/g,'ا').replace(/ة/g,'ه').replace(/ى/g,'ي').replace(/[٠-٩]/g, (d)=>'٠١٢٣٤٥٦٧٨٩'.indexOf(d)).replace(/[^\p{L}\p{N}]+/gu,' ').replace(/\b(نسخه|الطبعه|طبعة|pdf)\b/g,' ').replace(/\s+/g,' ').trim();
const tokens = (title) => new Set(norm(title).split(' ').filter(Boolean));
const jaccard = (a,b) => { const A=tokens(a),B=tokens(b); const common=[...A].filter(x=>B.has(x)).length; return common/(new Set([...A,...B]).size||1); };
const exact = new Map();
for (const record of records) { const key=norm(record.title); if (key) exact.set(key,[...(exact.get(key)??[]),record]); }
const groups = [...exact.values()].filter(g=>g.length>1).map((records)=>({kind:'exact_normalized',score:1,records}));
const usedPairs=new Set();
for(let i=0;i<records.length;i++) for(let j=i+1;j<records.length;j++) {
  const score=jaccard(records[i].title,records[j].title);
  if(score>=0.84 && norm(records[i].title)!==norm(records[j].title)) {
    const ids=[records[i].id,records[j].id].sort().join('|'); if(!usedPairs.has(ids)) { usedPairs.add(ids); groups.push({kind:'near_title',score,records:[records[i],records[j]]}); }
  }
}
const clean = groups.map((group,index)=>({group_id:index+1,kind:group.kind,score:Number(group.score.toFixed(3)),records:group.records.map(r=>({id:r.id,title:r.title,author:r.author,category:r.category,material_type:r.material_type,file_type:r.file_type,link_telegram:r.link_telegram,link_drive:r.link_drive,link_direct:r.link_direct,year:r.year}))}));
writeFileSync(path.join(root,'ibrazx40_duplicate_candidates.json'),`${JSON.stringify({total_groups:clean.length,groups:clean},null,2)}\n`);
console.log(JSON.stringify({total_groups:clean.length,exact_groups:clean.filter(g=>g.kind==='exact_normalized').length,near_groups:clean.filter(g=>g.kind==='near_title').length},null,2));
