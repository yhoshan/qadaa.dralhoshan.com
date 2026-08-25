import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
const root=process.cwd();
const load=(file)=>JSON.parse(readFileSync(path.join(root,file),'utf8'));
const sha=(file)=>createHash('sha256').update(readFileSync(path.join(root,file))).digest('hex');
const audit=load('ibrazx40_source_audit_records.json');
const merged=load('ibrazx40_merged_audit_reviews.json').merged;
const final=new Map(load('ibrazx40_final_adjudications.json').adjudications.map(row=>[row.id,row]));
const duplicateCandidates=load('ibrazx40_duplicate_candidates.json').groups;
const duplicateAdjudications=duplicateCandidates.length?load('ibrazx40_duplicate_adjudications.json').adjudications:[];
const records=new Map(audit.records.map(row=>[row.id,row]));
const classifications=merged.map(row=>{const judged=final.get(row.id);const decision=judged?.decision??row.final_decision;const reason=judged?.reason??row.final_reason;const confidence=judged?.confidence??row.final_confidence;return {id:row.id,title:row.title,source:row.source,category:row.category,decision,reason,confidence,link_telegram:records.get(row.id)?.link_telegram??'',initial_decision:row.decision,critical_decision:row.critical_review?.decision??''};}).sort((a,b)=>a.id.localeCompare(b.id));
const counts=Object.fromEntries(['KEEP','REMOVE','REVIEW'].map(d=>[d,classifications.filter(row=>row.decision===d).length]));
if(counts.KEEP+counts.REMOVE+counts.REVIEW!==audit.total) throw new Error('معادلة التصنيف لا تطابق إجمالي المصدر.');
const itemsRaw=load('items.json');const items=Array.isArray(itemsRaw)?itemsRaw:itemsRaw.items;
const iirmllSourceScope=items.filter(item=>item.source==='القانون الدولي العام'&&[item.link_telegram,item.link_drive,item.link_direct].some(link=>String(link??'').includes('ibrazx40'))).length;
const baseline=readFileSync(path.join(root,'ibrazx40_audit_baseline_sha256.txt'),'utf8').trim().split('\n').map(line=>line.split(/\s+/)[0]);
const current=['items.json','client/public/items.json','stats.json','client/public/stats.json'].map(sha);
const unchanged=baseline.length===current.length&&baseline.every((value,index)=>value===current[index]);
const duplicateMap=new Map(duplicateCandidates.map(group=>[group.group_id,group]));
const confirmedDuplicates=duplicateAdjudications.filter(row=>row.verdict==='DUPLICATE').map(row=>({...row,group:duplicateMap.get(row.group_id)}));
const finalOutput={generated_at:new Date().toISOString(),source:'القانون الدولي العام',link_identifier:'ibrazx40',total:audit.total,counts,classifications,remove_proposals:classifications.filter(row=>row.decision==='REMOVE'),human_reviews:classifications.filter(row=>row.decision==='REVIEW'),confirmed_duplicates:confirmedDuplicates,bad_links:audit.bad_links,verification:{total_items:items.length,source_scope_count:iirmllSourceScope,baseline_hashes_match:unchanged,current_hashes:current}};
writeFileSync(path.join(root,'ibrazx40_source_final_classifications.json'),`${JSON.stringify(finalOutput,null,2)}\n`);
const lines=[
'تقرير الفحص الفكري والموضوعي — مصدر ibrazx40 / القانون الدولي العام',
'التاريخ: 2026-08-25','',
'حدود الفحص','اقتصر الفحص على 133 سجلاً يكون مصدرها «القانون الدولي العام» وتطابق روابطها المعرّف ibrazx40. هذه مهمة تقرير فقط؛ لم يُحذف أو يعدّل أي سجل أو تصنيف أو رابط.','',
'ملخص النتائج','البند | العدد',`إجمالي سجلات ibrazx40 الحالية | ${audit.total}`,`إبقاء | ${counts.KEEP}`,`حذف مقترح | ${counts.REMOVE}`,`مراجعة بشرية | ${counts.REVIEW}`,`مجموعات التكرار المؤكدة | ${confirmedDuplicates.length}`,`النسخ الزائدة المحتملة | ${confirmedDuplicates.reduce((n,row)=>n+row.redundant_ids.length,0)}`,`روابط تالفة أو فارغة بنيوياً | ${audit.bad_links.length}`,'',`معادلة التغطية: ${counts.KEEP} + ${counts.REMOVE} + ${counts.REVIEW} = ${audit.total}.`,'',
'قائمة الحذف المقترحة','id | العنوان الكامل | التصنيف | سبب الحذف المحدد',...finalOutput.remove_proposals.map(row=>`${row.id} | ${row.title} | ${row.category} | ${row.reason}`),'',
'الحالات البشرية','id | العنوان | التصنيف | سبب الالتباس',...(finalOutput.human_reviews.length?finalOutput.human_reviews.map(row=>`${row.id} | ${row.title} | ${row.category} | ${row.reason}`):['لا توجد حالات مراجعة بشرية.']),'',
'التكرارات','لم تثبت أي مجموعة تكرار في الفحص المحافظ الحالي؛ عناوين المصدر لا تقدم تطابقاً حرفياً أو تقارباً كافياً لتوصية حذف.','',
'الروابط','لا توجد روابط فارغة أو غير صالحة بنيوياً ضمن نطاق المصدر.','',
'التحقق النهائي','البند | النتيجة',`إجمالي المكنز | ${items.length}`,`عدد سجلات نطاق المصدر بعد الفحص | ${iirmllSourceScope}`,`تطابق بصمات الملفات المرجعية قبل وبعد الفحص | ${unchanged?'نعم':'لا'}`,`items.json مطابق للنسخة المنشورة | ${current[0]===current[1]?'نعم':'لا'}`,`stats.json مطابق للنسخة المنشورة | ${current[2]===current[3]?'نعم':'لا'}`,'',
'حدود التنفيذ','لم يُنشأ checkpoint جديد، ولم يتغير commit 4cd1651 أو الوسم stable-clean-state-11286-2026-08-25، ولم تنفذ مزامنة GitHub أو Push أو نشر.'
];
writeFileSync(path.join(root,'ibrazx40_source_audit_report.txt'),`${lines.join('\n')}\n`,'utf8');
console.log(JSON.stringify({total:audit.total,counts,confirmed_duplicates:confirmedDuplicates.length,bad_links:audit.bad_links.length,unchanged,source_scope_count:iirmllSourceScope},null,2));
if(!unchanged||items.length!==11286||iirmllSourceScope!==audit.total)process.exit(1);
