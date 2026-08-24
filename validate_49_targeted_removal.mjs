import { readFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const targetIds = new Set([
  'legal_mag_196', 'legal_mag_201', 'legal_mag_202', 'legal_mag_203', 'legal_mag_204', 'legal_mag_207', 'legal_mag_208', 'legal_mag_212', 'legal_mag_213', 'legal_mag_217', 'legal_mag_227', 'legal_mag_233', 'legal_mag_237', 'legal_mag_238', 'legal_mag_239', 'legal_mag_240', 'legal_mag_241', 'legal_mag_242', 'legal_mag_244', 'legal_mag_245', 'legal_mag_246', 'legal_mag_252', 'legal_mag_259', 'legal_mag_260', 'legal_mag_261', 'legal_mag_263', 'legal_mag_264', 'legal_mag_265', 'legal_mag_266', 'legal_mag_267', 'legal_mag_268', 'legal_mag_269', 'legal_mag_270', 'legal_mag_272', 'legal_mag_273', 'alexandria_cbz_9566', 'alexandria_cbz_30657', 'alexandria_cbz_64598', 'alexandria_cbz_24605', 'alexandria_cbz_63753', 'alexandria_cbz_20559', 'alexandria_cbz_28851', 'alexandria_cbz_22918', 'alexandria_cbz_9769', 'alexandria_cbz_22793', 'alexandria_cbz_61793', 'alexandria_cbz_26393', 'alexandria_cbz_30602', 'alexandria_cbz_62017',
]);
const load = (file) => JSON.parse(readFileSync(path.join(root, file), 'utf8'));
const asItems = (data) => Array.isArray(data) ? data : data.items;
const duplicates = (items) => [...new Set(items.map((item) => item.id).filter((id, index, all) => all.indexOf(id) !== index))];
const main = asItems(load('items.json'));
const published = asItems(load('client/public/items.json'));
const stats = load('stats.json');
const publicStats = load('client/public/stats.json');
const mainIds = new Set(main.map((item) => item.id));
const publicIds = new Set(published.map((item) => item.id));
const remainingTargetIds = [...targetIds].filter((id) => mainIds.has(id) || publicIds.has(id));
const idMismatches = [...mainIds].filter((id) => !publicIds.has(id)).concat([...publicIds].filter((id) => !mainIds.has(id)));
const missingRequired = main.filter((item) => !item?.id || !item?.title || !item?.source || !(item.link_telegram || item.link_drive || item.link_direct));
const checks = {
  main_total: main.length === 11540,
  published_total: published.length === 11540,
  stats_total: stats.total_items === 11540,
  public_stats_total: publicStats.total_items === 11540,
  target_ids_absent: remainingTargetIds.length === 0,
  no_duplicate_ids_main: duplicates(main).length === 0,
  no_duplicate_ids_published: duplicates(published).length === 0,
  main_and_published_match: idMismatches.length === 0,
  no_missing_required_fields: missingRequired.length === 0,
};
console.log(JSON.stringify({ checks, passed: Object.values(checks).every(Boolean), total: main.length, remaining_target_ids: remainingTargetIds, id_mismatches: idMismatches, duplicate_ids: duplicates(main), missing_required_fields: missingRequired.slice(0, 20).map((item) => ({ id: item.id, title: item.title })) }, null, 2));
if (!Object.values(checks).every(Boolean)) process.exitCode = 1;
