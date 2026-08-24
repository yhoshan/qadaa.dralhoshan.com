import { readFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const targets = new Set([
  'archive_4_20230212_20230212_2202', 'alexandria_cbz_22895', 'alexandria_cbz_24852',
  'alexandria_cbz_29818', 'alexandria_cbz_35915', 'alexandria_cbz_66124', 'arabialawer_18722',
  'alexandria_cbz_72662', 'alexandria_cbz_27440', 'alexandria_cbz_22448', 'alexandria_cbz_10902',
  'alexandria_cbz_18123', 'alexandria_cbz_10881', 'alexandria_cbz_11004', 'alexandria_cbz_15252',
  'alexandria_cbz_22258', 'qadaa_3218', 'alexandria_cbz_32176', 'alexandria_cbz_8450',
  'alexandria_cbz_27047',
]);

const load = (file) => JSON.parse(readFileSync(path.join(root, file), 'utf8'));
const asItems = (data) => Array.isArray(data) ? data : data.items;
const main = asItems(load('items.json'));
const published = asItems(load('client/public/items.json'));
const stats = load('stats.json');
const publicStats = load('client/public/stats.json');
const duplicateIds = (items) => [...new Set(items.map((item) => item.id).filter((id, index, ids) => ids.indexOf(id) !== index))];
const mainIds = new Set(main.map((item) => item.id));
const publicIds = new Set(published.map((item) => item.id));
const missingRequired = main.filter((item) => !item?.id || !item?.title || !item?.source || !(item.link_telegram || item.link_drive || item.link_direct));
const mismatchIds = [...mainIds].filter((id) => !publicIds.has(id)).concat([...publicIds].filter((id) => !mainIds.has(id)));

const checks = {
  main_count_is_15650: main.length === 15650,
  published_count_is_15650: published.length === 15650,
  stats_total_is_15650: stats.total_items === 15650,
  public_stats_total_is_15650: publicStats.total_items === 15650,
  target_ids_absent_from_main: [...targets].every((id) => !mainIds.has(id)),
  target_ids_absent_from_published: [...targets].every((id) => !publicIds.has(id)),
  no_duplicate_ids_main: duplicateIds(main).length === 0,
  no_duplicate_ids_published: duplicateIds(published).length === 0,
  main_and_published_id_sets_match: mismatchIds.length === 0,
  no_missing_required_fields: missingRequired.length === 0,
};

console.log(JSON.stringify({
  checks,
  target_count: targets.size,
  main_count: main.length,
  published_count: published.length,
  duplicate_ids_main: duplicateIds(main),
  duplicate_ids_published: duplicateIds(published),
  id_set_mismatch: mismatchIds,
  missing_required_fields: missingRequired.slice(0, 20).map((item) => ({ id: item.id, title: item.title })),
  passed: Object.values(checks).every(Boolean),
}, null, 2));

if (!Object.values(checks).every(Boolean)) process.exitCode = 1;
