import { readFile, writeFile } from 'node:fs/promises';

const root = process.cwd();
const candidates = JSON.parse(await readFile(`${root}/lawlibrary_recovery_candidates.json`, 'utf8')).candidates;
const validation = JSON.parse(await readFile(`${root}/lawlibrary_recovery_link_validation.json`, 'utf8'));
const validationById = new Map(validation.results.map((row) => [row.id, row]));
const selected = [];
const deferred = [];
for (const candidate of candidates) {
  const check = validationById.get(candidate.id);
  if (check?.status === 'ACCESSIBLE') selected.push({ ...candidate, validation: check });
  else deferred.push({ ...candidate, validation: check || { status: 'NOT_VALIDATED' } });
}
const byGroup = Object.fromEntries([...selected.reduce((map, item) => map.set(item.recovery_group, (map.get(item.recovery_group) || 0) + 1), new Map()).entries()]);
const byOriginSource = Object.fromEntries([...selected.reduce((map, item) => map.set(item.source || item.publisher || 'غير محدد', (map.get(item.source || item.publisher || 'غير محدد') || 0) + 1), new Map()).entries()].sort((a,b) => b[1] - a[1]));
const deferredByStatus = Object.fromEntries([...deferred.reduce((map, item) => map.set(item.validation.status, (map.get(item.validation.status) || 0) + 1), new Map()).entries()]);
const result = { created_at: new Date().toISOString(), total_candidates: candidates.length, selected_count: selected.length, deferred_count: deferred.length, by_group: byGroup, by_origin_source: byOriginSource, deferred_by_status: deferredByStatus, selected, deferred };
await writeFile(`${root}/lawlibrary_recovery_accessible_manifest.json`, `${JSON.stringify(result, null, 2)}\n`);
await writeFile(`${root}/lawlibrary_recovery_accessible_manifest.txt`, [
  'بيان استعادة روابط مكتبة القانون المفتوحة حالياً',
  `إجمالي المرشحات بعد منع التكرار: ${candidates.length}`,
  `روابط مؤكدة الفتح: ${selected.length}`,
  `روابط مؤجلة: ${deferred.length}`,
  '',
  'التوزيع بحسب مجموعة الإدخال:',
  ...Object.entries(byGroup).map(([group, count]) => `- ${group}: ${count}`),
  '',
  'التوزيع بحسب المصدر الأصلي:',
  ...Object.entries(byOriginSource).map(([source, count]) => `- ${source}: ${count}`),
  '',
  'أسباب التأجيل:',
  ...Object.entries(deferredByStatus).map(([status, count]) => `- ${status}: ${count}`),
].join('\n'));
console.log(JSON.stringify({ total_candidates: candidates.length, selected: selected.length, deferred: deferred.length, by_group: byGroup, deferred_by_status: deferredByStatus }, null, 2));
