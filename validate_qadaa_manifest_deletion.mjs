import fs from 'node:fs/promises';
import crypto from 'node:crypto';

const root = process.cwd();
const backup = `${root}/backups/qadaa_manifest_188_2026-09-06`;
const manifestPath = '/home/ubuntu/upload/pasted_file_RkJXqY_qadaa_delete_manifest.json';
const parse = async (file) => JSON.parse(await fs.readFile(file, 'utf8'));
const unwrap = (data) => Array.isArray(data) ? data : data.items;
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
const [manifest, beforeData, afterData, publicData, stats, publicStats, hero, navbar, footer, indexHtml, hook] = await Promise.all([
  parse(manifestPath),
  parse(`${backup}/items.json.before.json`),
  parse(`${root}/items.json`),
  parse(`${root}/client/public/items.json`),
  parse(`${root}/stats.json`),
  parse(`${root}/client/public/stats.json`),
  fs.readFile(`${root}/client/src/components/HeroSection.tsx`, 'utf8'),
  fs.readFile(`${root}/client/src/components/Navbar.tsx`, 'utf8'),
  fs.readFile(`${root}/client/src/components/Footer.tsx`, 'utf8'),
  fs.readFile(`${root}/client/index.html`, 'utf8'),
  fs.readFile(`${root}/client/src/hooks/useItems.ts`, 'utf8'),
]);
const before = unwrap(beforeData);
const after = unwrap(afterData);
const publicItems = unwrap(publicData);
const targetIds = new Set(manifest.items.map((item) => String(item.id)));
const expectedSurvivors = before.filter((item) => !targetIds.has(String(item.id)));
const afterIds = after.map((item) => String(item.id));
const duplicateIds = [...new Set(afterIds.filter((id, index) => afterIds.indexOf(id) !== index))];
const heroCounts = after.reduce((acc, item) => {
  acc[heroGroup(item.category)] += 1;
  return acc;
}, { qadaa: 0, nizam: 0, mohama: 0 });
const recomputed = {
  categories: countBy(after, (item) => item.category),
  sources: countBy(after, (item) => item.source),
  material_types: countBy(after, (item) => item.material_type),
  file_types: countBy(after, (item) => item.file_type),
  featured_count: after.filter((item) => item.is_featured === true).length,
  with_download_links: after.filter((item) => Number(item.download_links_count ?? 0) > 0 || item.link_telegram || item.link_drive || item.link_direct).length,
};
const newDescription = 'فهرس بحثي يجمع العناوين والروابط في القضاء والأنظمة والمحاماة، ويشمل مواد سعودية وعربية ومقارنة.';
const newDisclaimer = 'وتشمل مواد المكنز مصادر من دول وأنظمة قانونية متعددة، ولا تدل فهرسة المادة أو إتاحتها على سريانها في المملكة العربية السعودية أو اعتماد مضمونها.';
const checks = {
  manifest_count_is_188: manifest.count === 188 && manifest.items.length === 188 && targetIds.size === 188,
  final_main_count_is_17172: after.length === 17172,
  final_public_count_is_17172: publicItems.length === 17172,
  no_manifest_id_remains: !afterIds.some((id) => targetIds.has(id)),
  main_and_public_items_match: hash(after) === hash(publicItems),
  all_non_target_records_preserved: hash(expectedSurvivors) === hash(after),
  no_duplicate_ids: duplicateIds.length === 0,
  main_stats_total_matches: stats.total_items === after.length,
  public_stats_match_main: hash(stats) === hash(publicStats),
  stats_categories_match: hash(stats.categories) === hash(recomputed.categories),
  stats_sources_match: hash(stats.sources) === hash(recomputed.sources),
  stats_material_types_match: hash(stats.material_types) === hash(recomputed.material_types),
  stats_file_types_match: hash(stats.file_types) === hash(recomputed.file_types),
  stats_featured_match: stats.featured_count === recomputed.featured_count,
  stats_download_links_match: stats.with_download_links === recomputed.with_download_links,
  hero_counts_match: stats.qadaa_count === heroCounts.qadaa && stats.nizam_count === heroCounts.nizam && stats.mohama_count === heroCounts.mohama && heroCounts.qadaa + heroCounts.nizam + heroCounts.mohama === after.length,
  hero_description_updated: hero.includes(newDescription),
  index_description_updated: indexHtml.includes(newDescription),
  disclaimer_updated: navbar.includes(newDisclaimer),
  old_scientific_label_removed: !footer.includes('فهرس علمي شامل'),
  old_fixed_share_number_removed: !footer.includes('11,000') && !footer.includes('أكثر من 11'),
  share_text_is_research_index: footer.includes('فهرس بحثي'),
  cache_buster_updated: hook.includes('qadaa-manifest-188-removal-2026-09-06'),
};
const report = {
  validated_at: new Date().toISOString(),
  before_count: before.length,
  requested_removal_count: targetIds.size,
  after_count: after.length,
  removed_count: before.length - after.length,
  remaining_target_ids: afterIds.filter((id) => targetIds.has(id)),
  duplicate_ids: duplicateIds,
  hero_counts: heroCounts,
  checks,
  success: Object.values(checks).every(Boolean),
};
await fs.writeFile(`${root}/qadaa_manifest_deletion_validation.json`, `${JSON.stringify(report, null, 2)}\n`);
await fs.writeFile(`${root}/qadaa_manifest_deletion_validation.txt`, [
  'فحص ما بعد تنفيذ قائمة الحذف المحددة',
  `تاريخ الفحص: ${report.validated_at}`,
  `قبل الحذف: ${report.before_count.toLocaleString('en-US')}`,
  `المطلوب حذفه: ${report.requested_removal_count.toLocaleString('en-US')}`,
  `المحذوف فعلياً: ${report.removed_count.toLocaleString('en-US')}`,
  `بعد الحذف: ${report.after_count.toLocaleString('en-US')}`,
  `المعرّفات المتبقية من القائمة: ${report.remaining_target_ids.length}`,
  `نجاح الفحص: ${report.success ? 'نعم' : 'لا'}`,
  '',
  ...Object.entries(checks).map(([name, passed]) => `${passed ? '[PASS]' : '[FAIL]'} ${name}`),
].join('\n'));
console.log(JSON.stringify({ success: report.success, before_count: report.before_count, removed_count: report.removed_count, after_count: report.after_count, remaining_target_ids: report.remaining_target_ids.length }, null, 2));
if (!report.success) process.exitCode = 1;
