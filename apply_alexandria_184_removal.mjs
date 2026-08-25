import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const precheck = JSON.parse(readFileSync(path.join(root, 'alexandria_184_removal_precheck.json'), 'utf8'));
if (!precheck.safe_to_apply) throw new Error('فشل التحقق المسبق؛ لن يتم الحذف.');
const targetIds = new Set(precheck.found.map((item) => item.id));
const load = (file) => JSON.parse(readFileSync(path.join(root, file), 'utf8'));
const unwrap = (data) => Array.isArray(data) ? { items: data, wrapper: null } : { items: data.items ?? [], wrapper: data };
const rewrap = ({ items, wrapper }) => wrapper ? { ...wrapper, items } : items;
const normalize = (value) => String(value ?? '').replace(/[أإآ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه').replace(/\s+/g, ' ').trim().toLowerCase();
const isAlexandria = (item) => normalize(item.source) === 'مكتبه الاسكندريه';
const mainData = unwrap(load('items.json'));
const publicData = unwrap(load('client/public/items.json'));
const currentFound = mainData.items.filter((item) => targetIds.has(item.id));
const currentFoundPublic = publicData.items.filter((item) => targetIds.has(item.id));
if (currentFound.length !== precheck.found_count || currentFoundPublic.length !== precheck.found_count) {
  throw new Error('تغيرت قائمة المعرفات بعد التحقق؛ أوقف الحذف لحماية البيانات.');
}
if (currentFound.some((item) => !isAlexandria(item)) || currentFoundPublic.some((item) => !isAlexandria(item))) {
  throw new Error('توقف آمن: ظهر معرف بمصدر غير مكتبة الإسكندرية.');
}

const nextMain = mainData.items.filter((item) => !targetIds.has(item.id));
const nextPublic = publicData.items.filter((item) => !targetIds.has(item.id));
const expectedTotal = precheck.before_count - precheck.found_count;
if (nextMain.length !== expectedTotal || nextPublic.length !== expectedTotal) {
  throw new Error('فشل تحقق العدد النهائي؛ لن تتم الكتابة.');
}
const countBy = (items, selector) => Object.fromEntries([...items.reduce((map, item) => {
  const key = selector(item) || 'غير مصنف';
  map.set(key, (map.get(key) ?? 0) + 1);
  return map;
}, new Map())].sort((a, b) => String(a[0]).localeCompare(String(b[0]), 'ar')));
const category = (item) => String(item.category ?? '');
const stats = {
  total_items: nextMain.length,
  qadaa_count: nextMain.filter((item) => /قضاء|قضائي/.test(category(item))).length,
  nizam_count: nextMain.filter((item) => /نظام|لائحة|تشريع/.test(category(item))).length,
  mohama_count: nextMain.filter((item) => /محاماة|محامي/.test(category(item))).length,
  other_count: 0,
  books_count: nextMain.length,
  audio_count: 0,
  video_count: 0,
  categories: countBy(nextMain, (item) => item.category),
  sources: countBy(nextMain, (item) => item.source),
  file_types: countBy(nextMain, (item) => item.file_type),
  featured_count: nextMain.filter((item) => item.is_featured).length,
  with_download_links: nextMain.filter((item) => item.link_telegram || item.link_drive || item.link_direct).length,
};
stats.other_count = Math.max(0, stats.total_items - stats.qadaa_count - stats.nizam_count - stats.mohama_count);
writeFileSync(path.join(root, 'items.json'), `${JSON.stringify(rewrap({ ...mainData, items: nextMain }), null, 2)}\n`);
writeFileSync(path.join(root, 'client/public/items.json'), `${JSON.stringify(rewrap({ ...publicData, items: nextPublic }), null, 2)}\n`);
writeFileSync(path.join(root, 'stats.json'), `${JSON.stringify(stats, null, 2)}\n`);
writeFileSync(path.join(root, 'client/public/stats.json'), `${JSON.stringify(stats, null, 2)}\n`);
const hookPath = path.join(root, 'client/src/hooks/useItems.ts');
const hook = readFileSync(hookPath, 'utf8');
const cacheVersion = 'alexandria-removal-184-2026-08-24';
writeFileSync(hookPath, hook.replace(/v=[^'"`)+]+/g, `v=${cacheVersion}`));
const remaining = nextMain.filter((item) => targetIds.has(item.id)).map((item) => item.id);
const duplicateIds = [...new Set(nextMain.map((item) => item.id).filter((id, index, ids) => ids.indexOf(id) !== index))];
const execution = {
  generated_at: new Date().toISOString(),
  before_count: precheck.before_count,
  requested_count: precheck.requested_count,
  found_count: precheck.found_count,
  missing_count: precheck.missing_count,
  removed_count: currentFound.length,
  final_count: nextMain.length,
  backup_dir: precheck.backup_dir,
  removed: currentFound.map((item) => ({ id: item.id, title: item.title, source: item.source, category: item.category })),
  missing: precheck.missing,
  remaining_target_ids: remaining,
  duplicate_ids_after_removal: duplicateIds,
  non_target_records_preserved_by_count: nextMain.length === expectedTotal,
  cache_version: cacheVersion,
};
writeFileSync(path.join(root, 'alexandria_184_removal_execution_report.json'), `${JSON.stringify(execution, null, 2)}\n`);
console.log(JSON.stringify({ before_count: execution.before_count, requested_count: execution.requested_count, found_count: execution.found_count, removed_count: execution.removed_count, final_count: execution.final_count, missing_count: execution.missing_count }, null, 2));
