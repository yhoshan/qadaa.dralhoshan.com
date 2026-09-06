import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';

const root = process.cwd();
const manifestPath = '/home/ubuntu/upload/pasted_file_RkJXqY_qadaa_delete_manifest.json';
const precheckPath = path.join(root, 'qadaa_delete_manifest_precheck.json');
const parse = async (file) => JSON.parse(await fs.readFile(file, 'utf8'));
const unwrap = (data) => Array.isArray(data) ? { items: data, wrapper: null } : { items: data.items ?? [], wrapper: data };
const rewrap = ({ items, wrapper }) => wrapper ? { ...wrapper, items } : items;
const hash = (value) => crypto.createHash('sha256').update(JSON.stringify(value)).digest('hex');
const countBy = (items, selector) => Object.fromEntries([...items.reduce((map, item) => {
  const key = String(selector(item) || 'غير مصنف');
  map.set(key, (map.get(key) ?? 0) + 1);
  return map;
}, new Map())].sort((a, b) => a[0].localeCompare(b[0], 'ar')));
const heroGroup = (category = '') => {
  const value = String(category);
  if (/(محام|تحكيم|وساط)/u.test(value)) return 'mohama';
  if (/(قضاء|قضائي|محكم|مرافع|إثبات|جنا|جزائي|حسبة|مظالم|أحكام|إجراء.*قضائي|قرار.*قضائي)/u.test(value)) return 'qadaa';
  return 'nizam';
};

const [manifest, precheck, mainRaw, publicRaw] = await Promise.all([
  parse(manifestPath),
  parse(precheckPath),
  parse(path.join(root, 'items.json')),
  parse(path.join(root, 'client/public/items.json')),
]);
const mainData = unwrap(mainRaw);
const publicData = unwrap(publicRaw);
const targets = manifest.items;
const targetIds = new Set(targets.map((item) => String(item.id)));
if (!precheck.all_verified || manifest.count !== 188 || targets.length !== 188 || targetIds.size !== 188) {
  throw new Error('فشل تحقق قائمة الحذف؛ لم تُكتب أي بيانات.');
}
if (mainData.items.length !== 17360 || publicData.items.length !== 17360 || hash(mainData.items) !== hash(publicData.items)) {
  throw new Error('تغيرت قاعدة البيانات منذ الفحص المسبق؛ لم تُكتب أي بيانات.');
}
const mainMatched = mainData.items.filter((item) => targetIds.has(String(item.id)));
const publicMatched = publicData.items.filter((item) => targetIds.has(String(item.id)));
if (mainMatched.length !== 188 || publicMatched.length !== 188 || !mainMatched.every((item) => targetIds.has(String(item.id)))) {
  throw new Error('قائمة المعرّفات لم تطابق 188 سجلاً بالضبط؛ لم تُكتب أي بيانات.');
}
const finalMain = mainData.items.filter((item) => !targetIds.has(String(item.id)));
const finalPublic = publicData.items.filter((item) => !targetIds.has(String(item.id)));
if (finalMain.length !== 17172 || finalPublic.length !== 17172 || finalMain.length !== mainData.items.length - mainMatched.length) {
  throw new Error('فشل تحقق العدد النهائي؛ لم تُكتب أي بيانات.');
}
const heroCounts = finalMain.reduce((acc, item) => {
  acc[heroGroup(item.category)] += 1;
  return acc;
}, { qadaa: 0, nizam: 0, mohama: 0 });
if (heroCounts.qadaa + heroCounts.nizam + heroCounts.mohama !== finalMain.length) throw new Error('فشل تقسيم بطاقات الإحصاء؛ لم تُكتب أي بيانات.');
const stats = {
  total_items: finalMain.length,
  categories: countBy(finalMain, (item) => item.category),
  sources: countBy(finalMain, (item) => item.source),
  material_types: countBy(finalMain, (item) => item.material_type),
  file_types: countBy(finalMain, (item) => item.file_type),
  featured_count: finalMain.filter((item) => item.is_featured === true).length,
  with_download_links: finalMain.filter((item) => Number(item.download_links_count ?? 0) > 0 || item.link_telegram || item.link_drive || item.link_direct).length,
  qadaa_count: heroCounts.qadaa,
  nizam_count: heroCounts.nizam,
  mohama_count: heroCounts.mohama,
};
const cacheVersion = 'qadaa-manifest-188-removal-2026-09-06';
const hookPath = path.join(root, 'client/src/hooks/useItems.ts');
const hook = await fs.readFile(hookPath, 'utf8');
const updatedHook = hook.replace(/v=[^'"`)+]+/g, `v=${cacheVersion}`);
if (updatedHook === hook) throw new Error('لم تُحدّث معلمة كسر الكاش؛ لم تُكتب أي بيانات.');

await Promise.all([
  fs.writeFile(path.join(root, 'items.json'), `${JSON.stringify(rewrap({ ...mainData, items: finalMain }), null, 2)}\n`),
  fs.writeFile(path.join(root, 'client/public/items.json'), `${JSON.stringify(rewrap({ ...publicData, items: finalPublic }), null, 2)}\n`),
  fs.writeFile(path.join(root, 'stats.json'), `${JSON.stringify(stats, null, 2)}\n`),
  fs.writeFile(path.join(root, 'client/public/stats.json'), `${JSON.stringify(stats, null, 2)}\n`),
  fs.writeFile(hookPath, updatedHook),
]);

const finalIds = new Set(finalMain.map((item) => String(item.id)));
const duplicateIds = [...new Set(finalMain.map((item) => String(item.id)).filter((id, index, ids) => ids.indexOf(id) !== index))];
const report = {
  generated_at: new Date().toISOString(),
  before_count: mainData.items.length,
  requested_count: targets.length,
  found_count: mainMatched.length,
  removed_count: mainMatched.length,
  final_count: finalMain.length,
  expected_final_count: 17172,
  remaining_target_ids: [...targetIds].filter((id) => finalIds.has(id)),
  main_public_match_after: hash(finalMain) === hash(finalPublic),
  duplicate_ids_after: duplicateIds,
  non_target_records_preserved_by_count: finalMain.length === mainData.items.length - mainMatched.length,
  removed_records: mainMatched.map((item) => ({ id: item.id, title: item.title, source: item.source, category: item.category })),
  removed_by_source: countBy(mainMatched, (item) => item.source),
  stats,
  cache_version: cacheVersion,
};
await fs.writeFile(path.join(root, 'qadaa_manifest_deletion_execution.json'), `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify({ before_count: report.before_count, removed_count: report.removed_count, final_count: report.final_count, remaining_target_ids: report.remaining_target_ids.length, main_public_match_after: report.main_public_match_after, duplicate_ids_after: report.duplicate_ids_after.length }, null, 2));
