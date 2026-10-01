import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const sourceName = 'وزارة العدل السعودية — البوابة القانونية';
const backupDir = path.join(root, 'backups/moj_documentation_2026-09-28');
const candidatePath = path.join(root, 'moj_documentation_2026-09-28_candidates.json');
function sha256(value) { return crypto.createHash('sha256').update(value).digest('hex'); }
function normalizeArabic(text = '') {
  return String(text).replace(/[أإآا]/g, 'ا').replace(/[\u064B-\u065F]/g, '').replace(/ة/g, 'ه').replace(/ى/g, 'ي').toLowerCase().trim();
}
function countBy(list, field) {
  const counts = list.reduce((acc, item) => { const v = item[field] || ''; if (v) acc[v] = (acc[v] || 0) + 1; return acc; }, {});
  return Object.fromEntries(Object.entries(counts).sort(([a, ac], [b, bc]) => bc - ac || a.localeCompare(b, 'ar')));
}
function heroGroup(category = '') {
  if (/(محام|تحكيم|وساط)/u.test(category)) return 'mohama';
  if (/(قضاء|قضائي|محكم|مرافع|إثبات|جنا|جزائي|حسبة|مظالم|أحكام|إجراء.*قضائي|قرار.*قضائي)/u.test(category)) return 'qadaa';
  return 'nizam';
}
const [mainText, publicText, statsText, publicStatsText, beforeText, candidatesText, cache] = await Promise.all([
  fs.readFile(path.join(root, 'items.json'), 'utf8'),
  fs.readFile(path.join(root, 'client/public/items.json'), 'utf8'),
  fs.readFile(path.join(root, 'stats.json'), 'utf8'),
  fs.readFile(path.join(root, 'client/public/stats.json'), 'utf8'),
  fs.readFile(path.join(backupDir, 'items.before.json'), 'utf8'),
  fs.readFile(candidatePath, 'utf8'),
  fs.readFile(path.join(root, 'client/src/hooks/useItems.ts'), 'utf8'),
]);
const items = JSON.parse(mainText);
const before = JSON.parse(beforeText);
const candidates = JSON.parse(candidatesText);
const stats = JSON.parse(statsText);
if (!Array.isArray(items) || !Array.isArray(before) || !Array.isArray(candidates)) throw new Error('بنية JSON غير متوقعة');
const expectedIds = candidates.map((item) => item.id);
const actualNew = items.filter((item) => String(item.id).startsWith('moj_docs_'));
const duplicateIds = items.map((item) => item.id).filter((id, index, all) => all.indexOf(id) !== index);
const originalIntegrity = before.every((item, index) => JSON.stringify(item) === JSON.stringify(items[index]));
const expectedStats = {
  total_items: items.length,
  categories: countBy(items, 'category'),
  sources: countBy(items, 'source'),
  material_types: countBy(items, 'material_type'),
  file_types: countBy(items, 'file_type'),
  featured_count: items.filter((item) => item.is_featured).length,
  with_download_links: items.filter((item) => Number(item.download_links_count || 0) > 0).length,
};
const hero = items.reduce((out, item) => { out[heroGroup(item.category)] += 1; return out; }, { qadaa: 0, nizam: 0, mohama: 0 });
const searchHits = items.filter((item) => normalizeArabic([item.title, item.author, item.investigator, item.category, item.source].join(' ')).includes(normalizeArabic('شرح نظام المعاملات المدنية')));
const materialTypeHits = actualNew.filter((item) => item.material_type === 'شرح');
const report = {
  validated_at: new Date().toISOString(),
  data_files_identical: mainText === publicText,
  stats_files_identical: statsText === publicStatsText,
  before_total: before.length,
  after_total: items.length,
  added_total: items.length - before.length,
  expected_ids: expectedIds,
  actual_new_ids: actualNew.map((item) => item.id),
  exact_expected_records_present: expectedIds.every((id) => items.some((item) => item.id === id)),
  official_source_count: items.filter((item) => item.source === sourceName).length,
  original_records_unchanged_and_in_order: originalIntegrity,
  duplicate_ids: duplicateIds,
  stats_match_recalculation: JSON.stringify(expectedStats) === JSON.stringify({
    total_items: stats.total_items,
    categories: stats.categories,
    sources: stats.sources,
    material_types: stats.material_types,
    file_types: stats.file_types,
    featured_count: stats.featured_count,
    with_download_links: stats.with_download_links,
  }),
  hero_counts_match_stats: hero.qadaa === stats.qadaa_count && hero.nizam === stats.nizam_count && hero.mohama === stats.mohama_count && hero.qadaa + hero.nizam + hero.mohama === items.length,
  cache_buster_updated: cache.includes('moj-official-documents-2026-09-28'),
  search_test: { query: 'شرح نظام المعاملات المدنية', result_count: searchHits.length, expected_new_ids: actualNew.filter((item) => item.title.includes('شرح نظام المعاملات المدنية')).map((item) => item.id) },
  material_type_filter_test: { value: 'شرح', matching_new_ids: materialTypeHits.map((item) => item.id) },
  additions: actualNew.map((item) => ({ id: item.id, title: item.title, link_direct: item.link_direct, pages_count: item.pages_count, file_size: item.file_size })),
  file_hashes: { items_json: sha256(mainText), public_items_json: sha256(publicText), stats_json: sha256(statsText), public_stats_json: sha256(publicStatsText) },
};
const failed = [
  ['تطابق نسختي المواد', report.data_files_identical],
  ['تطابق نسختي الإحصاءات', report.stats_files_identical],
  ['ست إضافات بالضبط', report.added_total === 6 && report.actual_new_ids.length === 6],
  ['وجود المعرّفات المتوقعة', report.exact_expected_records_present],
  ['عدد المصدر الرسمي', report.official_source_count === 6],
  ['سلامة السجلات السابقة', report.original_records_unchanged_and_in_order],
  ['عدم وجود معرّفات مكررة', report.duplicate_ids.length === 0],
  ['مطابقة الإحصاءات', report.stats_match_recalculation],
  ['مطابقة بطاقات Hero', report.hero_counts_match_stats],
  ['تحديث كسر الكاش', report.cache_buster_updated],
].filter(([, pass]) => !pass);
report.passed = failed.length === 0;
report.failed_checks = failed.map(([name]) => name);
await fs.writeFile(path.join(root, 'moj_documentation_2026-09-28_validation.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
if (!report.passed) process.exit(1);
