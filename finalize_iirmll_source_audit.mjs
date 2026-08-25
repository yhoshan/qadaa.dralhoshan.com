import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const load = (file) => JSON.parse(readFileSync(path.join(root, file), 'utf8'));
const sha256 = (file) => createHash('sha256').update(readFileSync(path.join(root, file))).digest('hex');
const source = load('iirmll_source_audit_records.json');
const initial = load('iirmll_source_initial_classifications.json').classifications;
const critical = load('iirmll_critical_reviews.json').reviews;
const adjudications = load('iirmll_final_adjudications.json').adjudications;
const duplicates = load('iirmll_duplicate_conservative_adjudications.json');
const reference = load('stable_state_pre_restart_verification.json');
const criticalById = new Map(critical.filter((row) => row.critical).map((row) => [row.id, row.critical]));
const adjudicationById = new Map(adjudications.filter((row) => row.adjudication).map((row) => [row.id, row.adjudication]));
const recordById = new Map(source.records.map((record) => [record.id, record]));
const classifications = initial.map((row) => {
  let decision = row.decision;
  let reason = row.reason;
  let confidence = row.confidence;
  let stage = 'الفحص الأولي';
  const criticalVerdict = criticalById.get(row.id);
  if (criticalVerdict) {
    decision = criticalVerdict.decision;
    reason = criticalVerdict.reason;
    confidence = criticalVerdict.confidence;
    stage = 'المراجعة النقدية';
  }
  const finalVerdict = adjudicationById.get(row.id);
  if (finalVerdict) {
    decision = finalVerdict.decision;
    reason = finalVerdict.reason;
    confidence = finalVerdict.confidence;
    stage = 'التحكيم النهائي';
  }
  const record = recordById.get(row.id);
  return { id: row.id, title: row.title, decision, reason, confidence, stage, source: record.source, category: record.category, links: record.links };
});
const counts = Object.fromEntries(['KEEP', 'REMOVE', 'REVIEW'].map((decision) => [decision, classifications.filter((row) => row.decision === decision).length]));
const removals = classifications.filter((row) => row.decision === 'REMOVE');
const human = classifications.filter((row) => row.decision === 'REVIEW');
const files = ['items.json', 'client/public/items.json', 'stats.json', 'client/public/stats.json'];
const currentHashes = Object.fromEntries(files.map((file) => [file, sha256(file)]));
const referenceMatch = Object.fromEntries(files.map((file) => [file, currentHashes[file] === reference.files[file].sha256]));
const structuralIssues = source.invalid_links;
const scopeOk = classifications.every((row) => row.source === 'المكتبة القانونية ⚖️' && String(row.links?.link_telegram ?? '').includes('t.me/iirmll/'));
const confirmedDuplicates = duplicates.confirmed_groups;
const redundantCount = confirmedDuplicates.reduce((total, group) => total + group.redundant_ids.length, 0);
const allIds = new Set(source.records.map((record) => record.id));
const classificationCoverage = classifications.length === source.selected_count && classifications.every((row) => allIds.has(row.id));
const validation = {
  total_source_records: source.selected_count,
  counts,
  equation_holds: counts.KEEP + counts.REMOVE + counts.REVIEW === source.selected_count,
  scope_ok: scopeOk,
  classification_coverage: classificationCoverage,
  reference_hash_match: referenceMatch,
  all_hashes_match: Object.values(referenceMatch).every(Boolean),
  invalid_link_count: structuralIssues.length,
  confirmed_duplicate_groups: confirmedDuplicates.length,
  potential_redundant_copies: redundantCount,
};
writeFileSync(path.join(root, 'iirmll_source_final_classifications.json'), `${JSON.stringify({ generated_at: new Date().toISOString(), validation, classifications, removals, human, confirmed_duplicates: confirmedDuplicates, duplicate_groups_not_confirmed: duplicates.unconfirmed_groups }, null, 2)}\n`);
const duplicateLines = confirmedDuplicates.length ? confirmedDuplicates.flatMap((group, index) => [
  `المجموعة ${index + 1} — ${group.group_id}`,
  `المعرفات: ${group.records.map((record) => record.id).join(' | ')}`,
  `العناوين: ${group.records.map((record) => `${record.id}: ${record.title}`).join(' | ')}`,
  `النسخة المقترح إبقاؤها: ${group.recommended_keep_id}`,
  `النسخ الزائدة المقترحة: ${group.redundant_ids.join(' | ')}`,
  `سبب ثبوت التكرار: ${group.reason}`,
  '',
]) : ['لا توجد مجموعات تكرار مؤكدة وفق معيار الإثبات المحافظ.', ''];
const lines = [
  'تقرير فحص فكري وموضوعي مشدد — مصدر iirmll / المكتبة القانونية',
  'التاريخ: 2026-08-25',
  '',
  'النطاق',
  'اقتصر الفحص على السجلات التي مصدرها «المكتبة القانونية ⚖️» ورابط تيليجرامها يتضمن t.me/iirmll/. لم يطال أي مصدر آخر ولم يُفتح أي رابط إلا فحصه بنيوياً.',
  '',
  'النتائج الرقمية',
  'البند | العدد',
  `إجمالي سجلات iirmll الحالية | ${source.selected_count}`,
  `إبقاء | ${counts.KEEP}`,
  `حذف مقترح | ${counts.REMOVE}`,
  `مراجعة بشرية | ${counts.REVIEW}`,
  `مجموعات التكرار المؤكدة | ${confirmedDuplicates.length}`,
  `النسخ الزائدة المحتملة | ${redundantCount}`,
  `روابط تالفة أو فارغة بنيوياً | ${structuralIssues.length}`,
  '',
  `معادلة التغطية: ${counts.KEEP} + ${counts.REMOVE} + ${counts.REVIEW} = ${source.selected_count} — ${validation.equation_holds ? 'صحيحة' : 'غير صحيحة'}.`,
  '',
  'قائمة الحذف المقترحة',
  ...(removals.length ? removals.map((row) => `${row.id} | ${row.title} | ${row.reason}`) : ['لا توجد مواد مقترحة للحذف.']),
  '',
  'الحالات البشرية',
  ...(human.length ? human.map((row) => `${row.id} | ${row.title} | ${row.reason}`) : ['لا توجد حالات مراجعة بشرية.']),
  '',
  'التكرارات المؤكدة — توصيات تنظيمية غير منفذة',
  ...duplicateLines,
  `مجموعات مرشحة لم تثبت كتكرار: ${duplicates.unconfirmed_groups.length}. لم توضع في قائمة النسخ الزائدة لأن تشابه العنوان أو الموضوع لا يكفي.`,
  '',
  'الروابط',
  ...(structuralIssues.length ? structuralIssues.map((row) => `${row.id} | ${row.title} | ${row.issue}`) : ['لا توجد روابط فارغة أو تالفة بنيوياً في سجلات النطاق.']),
  '',
  'التحقق النهائي من ثبات الحالة المرجعية',
  `إجمالي المكنز: ${source.total_main_items} مادة.`,
  `تطابق items.json والنسخة المنشورة: ${source.total_main_items === source.total_published_items ? 'نعم' : 'لا'}.`,
  ...files.map((file) => `${file}: ${referenceMatch[file] ? 'البصمة مطابقة للمرجع المحلي' : 'اختلاف في البصمة'}.`),
  `مرجع Git المحلي: bedebff — الوسم: stable-clean-state-11295-2026-08-25.`,
  '',
  'حدود التنفيذ',
  'هذا تقرير فقط. لم ينفذ حذف أو تعديل أو نقل أو إعادة تصنيف للبيانات، ولم تتغير الإحصاءات أو الواجهة، ولم يُنشأ checkpoint جديد أو مزامنة GitHub أو نشر.',
  '',
];
writeFileSync(path.join(root, 'iirmll_source_audit_report.txt'), lines.join('\n'), 'utf8');
console.log(JSON.stringify(validation, null, 2));
if (!validation.equation_holds || !validation.scope_ok || !validation.classification_coverage || !validation.all_hashes_match) process.exit(1);
