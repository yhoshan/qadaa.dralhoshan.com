import fs from 'node:fs/promises';
import crypto from 'node:crypto';

const root = process.cwd();
const paths = {
  itemsMain: `${root}/items.json`,
  itemsPublic: `${root}/client/public/items.json`,
  statsMain: `${root}/stats.json`,
  statsPublic: `${root}/client/public/stats.json`,
  beforeItems: `${root}/backups/marqoom_sadr_2026-09-06/items.main.json`,
  cache: `${root}/client/src/hooks/useItems.ts`,
};
const text = Object.fromEntries(await Promise.all(Object.entries(paths).map(async ([key, path]) => [key, await fs.readFile(path, 'utf8')])));
const itemsMainContainer = JSON.parse(text.itemsMain);
const itemsPublicContainer = JSON.parse(text.itemsPublic);
const statsMain = JSON.parse(text.statsMain);
const statsPublic = JSON.parse(text.statsPublic);
const beforeContainer = JSON.parse(text.beforeItems);
const itemsMain = Array.isArray(itemsMainContainer) ? itemsMainContainer : itemsMainContainer.items;
const itemsPublic = Array.isArray(itemsPublicContainer) ? itemsPublicContainer : itemsPublicContainer.items;
const beforeItems = Array.isArray(beforeContainer) ? beforeContainer : beforeContainer.items;

function hash(value) { return crypto.createHash('sha256').update(value).digest('hex'); }
function countBy(list, field) { return list.reduce((counts, item) => { const value = item[field] || ''; if (value) counts[value] = (counts[value] || 0) + 1; return counts; }, {}); }
function sortObject(value) {
  if (Array.isArray(value)) return value.map(sortObject);
  if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort((a, b) => a.localeCompare(b, 'ar')).map((key) => [key, sortObject(value[key])]));
  return value;
}
function sameObject(a, b) { return JSON.stringify(sortObject(a)) === JSON.stringify(sortObject(b)); }
const ids = itemsMain.map((item) => item.id);
const duplicateIds = [...new Set(ids.filter((id, index) => ids.indexOf(id) !== index))];
const currentById = new Map(itemsMain.map((item) => [item.id, item]));
const changedPriorRecords = beforeItems.filter((item) => !currentById.has(item.id) || !sameObject(item, currentById.get(item.id))).map((item) => item.id);
const newItems = itemsMain.filter((item) => !beforeItems.some((prior) => prior.id === item.id));
const marqoom = newItems.filter((item) => item.id.startsWith('marqoom_'));
const sadr = newItems.filter((item) => item.id.startsWith('sadr_'));
const statsExpected = {
  total_items: itemsMain.length,
  categories: countBy(itemsMain, 'category'),
  sources: countBy(itemsMain, 'source'),
  material_types: countBy(itemsMain, 'material_type'),
  file_types: countBy(itemsMain, 'file_type'),
  featured_count: itemsMain.filter((item) => item.is_featured).length,
  with_download_links: itemsMain.filter((item) => Number(item.download_links_count || 0) > 0).length,
};
const requiredKeys = ['id','title','author','investigator','publisher','year','link_telegram','link_drive','link_direct','source','category','material_type','file_type','file_size','pages_count','is_featured','download_links_count'];
const malformedNewRecords = newItems.filter((item) => requiredKeys.some((key) => !(key in item)) || !item.title || !item.source || !item.link_direct || item.download_links_count !== 1).map((item) => item.id);
const report = {
  checked_at: new Date().toISOString(),
  totals: { before: beforeItems.length, after: itemsMain.length, added: newItems.length, marqoom: marqoom.length, sadr: sadr.length },
  file_hashes: { items_main: hash(text.itemsMain), items_public: hash(text.itemsPublic), stats_main: hash(text.statsMain), stats_public: hash(text.statsPublic) },
  checks: {
    items_files_byte_identical: text.itemsMain === text.itemsPublic,
    stats_files_byte_identical: text.statsMain === text.statsPublic,
    items_json_equal: sameObject(itemsMainContainer, itemsPublicContainer),
    stats_json_equal: sameObject(statsMain, statsPublic),
    total_matches_stats: statsMain.total_items === itemsMain.length,
    stats_derived_fields_match: ['total_items','categories','sources','material_types','file_types','featured_count','with_download_links'].every((key) => sameObject(statsMain[key], statsExpected[key])),
    no_duplicate_ids: duplicateIds.length === 0,
    previous_records_preserved: changedPriorRecords.length === 0,
    expected_addition_count: newItems.length === 61 && marqoom.length === 27 && sadr.length === 34,
    all_new_records_complete: malformedNewRecords.length === 0,
    cache_buster_updated: text.cache.includes('marqoom-sadr-open-links-2026-09-06') && !text.cache.includes('promahmoud-source-reference-2026-09-06'),
  },
  anomalies: { duplicate_ids: duplicateIds, changed_prior_records: changedPriorRecords, malformed_new_records: malformedNewRecords },
  new_sources: countBy(newItems, 'source'),
  new_categories: countBy(newItems, 'category'),
};
report.success = Object.values(report.checks).every(Boolean);
await fs.writeFile(`${root}/marqoom_sadr_post_validation.json`, JSON.stringify(report, null, 2));
await fs.writeFile(`${root}/marqoom_sadr_post_validation.txt`, [
  `نجح الفحص: ${report.success ? 'نعم' : 'لا'}`,
  `الإجمالي قبل الإضافة: ${report.totals.before}`,
  `الإجمالي بعد الإضافة: ${report.totals.after}`,
  `المضاف: ${report.totals.added}`,
  `- شبكة مكتبة القانون: ${report.totals.marqoom}`,
  `- المركز السعودي للتحكيم التجاري (صدر): ${report.totals.sadr}`,
  '',
  ...Object.entries(report.checks).map(([name, passed]) => `${passed ? '[PASS]' : '[FAIL]'} ${name}`),
  '',
  `معرّفات مكررة: ${duplicateIds.length}`,
  `سجلات سابقة تغيّرت أو فُقدت: ${changedPriorRecords.length}`,
  `سجلات جديدة غير مكتملة: ${malformedNewRecords.length}`,
].join('\n'));
console.log(JSON.stringify({ success: report.success, ...report.totals }));
if (!report.success) process.exitCode = 1;
