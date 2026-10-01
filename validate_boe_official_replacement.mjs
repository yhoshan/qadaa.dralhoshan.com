import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const backup = path.join(root, 'backups/boe_official_replacement_2026-09-29');
const additionCsv = '/home/ubuntu/upload/pasted_file_rCwoBj_qadaa_add_boe_official_538.csv';
const deletionCsv = '/home/ubuntu/upload/pasted_file_ClHru3_qadaa_remove_intermediary_226.csv';
const manifestPath = '/home/ubuntu/upload/pasted_file_pN8Ytn_qadaa_boe_execution_manifest.json';
const reportPath = path.join(root, 'boe_official_replacement_2026-09-29_validation.json');
const officialPrefix = 'https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/';

function parseCsv(text) {
  const rows = []; let row = [], cell = '', quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (quoted) { if (ch === '"') { if (text[i + 1] === '"') { cell += '"'; i += 1; } else quoted = false; } else cell += ch; }
    else if (ch === '"') quoted = true;
    else if (ch === ',') { row.push(cell); cell = ''; }
    else if (ch === '\n') { row.push(cell.replace(/\r$/u, '')); rows.push(row); row = []; cell = ''; }
    else cell += ch;
  }
  if (cell || row.length) { row.push(cell.replace(/\r$/u, '')); rows.push(row); }
  const [header, ...body] = rows;
  return body.filter((r) => r.some((v) => v !== '')).map((r) => Object.fromEntries(header.map((h, i) => [h.replace(/^\uFEFF/u, ''), r[i] ?? ''])));
}
function unwrap(container) { return Array.isArray(container) ? container : container.items; }
function normalizeArabic(text = '') { return String(text).replace(/[أإآٱ]/gu, 'ا').replace(/ى/gu, 'ي').replace(/ة/gu, 'ه').replace(/[\u064B-\u065F\u0670\u0640]/gu, '').toLowerCase().trim(); }
function hash(value) { return crypto.createHash('sha256').update(value).digest('hex'); }

const [beforeText, finalText, publicText, statsText, publicStatsText, cacheText, addText, deleteText, manifestText] = await Promise.all([
  fs.readFile(path.join(backup, 'items.before.json'), 'utf8'), fs.readFile(path.join(root, 'items.json'), 'utf8'),
  fs.readFile(path.join(root, 'client/public/items.json'), 'utf8'), fs.readFile(path.join(root, 'stats.json'), 'utf8'),
  fs.readFile(path.join(root, 'client/public/stats.json'), 'utf8'), fs.readFile(path.join(root, 'client/src/hooks/useItems.ts'), 'utf8'),
  fs.readFile(additionCsv, 'utf8'), fs.readFile(deletionCsv, 'utf8'), fs.readFile(manifestPath, 'utf8'),
]);
const before = unwrap(JSON.parse(beforeText));
const final = unwrap(JSON.parse(finalText));
const publicItems = unwrap(JSON.parse(publicText));
const stats = JSON.parse(statsText);
const publicStats = JSON.parse(publicStatsText);
const additions = parseCsv(addText);
const deletions = parseCsv(deleteText);
const manifest = JSON.parse(manifestText);
const removed = new Set(deletions.map((r) => r.current_id));
const addBoeIds = new Set(additions.map((r) => r.boe_id));
const beforeById = new Map(before.map((x) => [x.id, x]));
const finalById = new Map(final.map((x) => [x.id, x]));
const beforeIds = new Set(beforeById);
const finalIds = new Set(finalById);
const missingRemovalIds = [...removed].filter((id) => finalIds.has(id));
const missingOfficialIds = [...addBoeIds].filter((boeId) => !finalById.has(`boe_${boeId}`));
const actualRemovedIds = [...beforeIds].filter((id) => !finalIds.has(id));
const actualAddedIds = [...finalIds].filter((id) => !beforeIds.has(id));
const duplicateIds = final.map((x) => x.id).filter((id, index, arr) => arr.indexOf(id) !== index);
const officialItems = final.filter((item) => String(item.id).startsWith('boe_'));
const officialBoeIds = officialItems.map((item) => item.boe_id);
const duplicateBoeIds = officialBoeIds.filter((id, index, arr) => arr.indexOf(id) !== index);
const protectedMoj = manifest.protected_moj.map((x) => x.id);
const changedNonTargets = [];
for (const [id, beforeItem] of beforeById) {
  if (removed.has(id)) continue;
  const afterItem = finalById.get(id);
  if (!afterItem || JSON.stringify(beforeItem) !== JSON.stringify(afterItem)) changedNonTargets.push(id);
}
const normalizedSearch = normalizeArabic('نظام التنفيذ');
const searchMatches = final.filter((item) => normalizeArabic([item.title,item.author,item.investigator,item.category,item.source].join(' ')).includes(normalizedSearch));
const officialExecutionHit = searchMatches.some((item) => item.id === 'boe_67dd54bc-c33a-48c8-8356-b44700a9ab55');
const typeFilterResults = final.filter((item) => item.material_type === 'نظام');

assert.equal(before.length, 17178);
assert.equal(final.length, 17490);
assert.equal(publicItems.length, 17490);
assert.equal(finalText, publicText, 'main and public item JSON must match byte-for-byte');
assert.equal(statsText, publicStatsText, 'main and public stats JSON must match byte-for-byte');
assert.equal(additions.length, 538);
assert.equal(addBoeIds.size, 538);
assert.equal(deletions.length, 226);
assert.equal(removed.size, 226);
assert.deepEqual(new Set(actualRemovedIds), removed, 'only listed current_id values may be removed');
assert.equal(actualRemovedIds.length, 226);
assert.equal(actualAddedIds.length, 538);
assert.deepEqual(new Set(actualAddedIds), new Set([...addBoeIds].map((id) => `boe_${id}`)), 'only expected BOE records may be added');
assert.equal(missingRemovalIds.length, 0);
assert.equal(missingOfficialIds.length, 0);
assert.equal(officialItems.length, 538);
assert.equal(new Set(officialBoeIds).size, 538);
assert.equal(duplicateIds.length, 0);
assert.equal(duplicateBoeIds.length, 0);
assert.ok(officialItems.every((item) => item.link_direct.startsWith(officialPrefix)));
assert.ok(protectedMoj.every((id) => finalById.has(id)));
assert.equal(changedNonTargets.length, 0, 'non-target records must remain unchanged');
assert.equal(stats.total_items, 17490);
assert.equal(stats.qadaa_count + stats.nizam_count + stats.mohama_count, 17490);
assert.ok(cacheText.includes('boe-official-canonical-538-2026-09-29'));
assert.ok(!cacheText.includes('moj-official-documents-2026-09-28'));
assert.ok(officialExecutionHit, 'Arabic-normalized search must find official Enforcement Law');
assert.ok(typeFilterResults.length >= 538, 'material type filter must include all official records');

const report = {
  validated_at: new Date().toISOString(),
  before_total: before.length,
  official_added: officialItems.length,
  intermediaries_removed: actualRemovedIds.length,
  after_total: final.length,
  no_listed_removal_id_remains: missingRemovalIds.length === 0,
  boe_id_duplicates: duplicateBoeIds.length,
  item_id_duplicates: duplicateIds.length,
  official_urls_valid: officialItems.filter((item) => item.link_direct.startsWith(officialPrefix)).length,
  protected_moj_preserved: protectedMoj.filter((id) => finalById.has(id)),
  non_target_records_changed: changedNonTargets.length,
  main_public_items_match: finalText === publicText,
  main_public_stats_match: statsText === publicStatsText,
  hero_counts: {qadaa: stats.qadaa_count, nizam: stats.nizam_count, mohama: stats.mohama_count},
  search_test: {query: 'نظام التنفيذ', normalized: normalizedSearch, match_count: searchMatches.length, official_execution_found: officialExecutionHit},
  material_type_filter_test: {value: 'نظام', result_count: typeFilterResults.length, all_official_records_match: officialItems.every((item) => item.material_type === 'نظام')},
  file_hashes: {items_json: hash(finalText), stats_json: hash(statsText)},
};
await fs.writeFile(reportPath, JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
