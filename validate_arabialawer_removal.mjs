import { readFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const load = (file) => JSON.parse(readFileSync(path.join(root, file), 'utf8'));
const asItems = (data) => Array.isArray(data) ? data : data.items;
const normalize = (value = '') => String(value)
  .normalize('NFKC').replace(/[أإآٱ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي')
  .replace(/[ً-ٟـ]/g, '').replace(/[\p{P}\p{S}\s_]/gu, '').toLowerCase();
const isTarget = (item) => {
  const idMatch = String(item.id ?? '').toLowerCase().startsWith('arabialawer_');
  const entityText = [item.source, item.publisher, item.organization, item.entity, item.institution, item.agency].filter(Boolean).join(' ');
  return idMatch || normalize(entityText).includes('arabialawer') || normalize(entityText).includes('اكاديميهالمحاماه');
};
const duplicates = (items) => [...new Set(items.map((item) => item.id).filter((id, index, ids) => ids.indexOf(id) !== index))];

const main = asItems(load('items.json'));
const published = asItems(load('client/public/items.json'));
const stats = load('stats.json');
const publicStats = load('client/public/stats.json');
const mainIds = new Set(main.map((item) => item.id));
const publishedIds = new Set(published.map((item) => item.id));
const idMismatches = [...mainIds].filter((id) => !publishedIds.has(id)).concat([...publishedIds].filter((id) => !mainIds.has(id)));
const missingRequired = main.filter((item) => !item?.id || !item?.title || !item?.source || !(item.link_telegram || item.link_drive || item.link_direct));

const checks = {
  expected_total_main: main.length === 11589,
  expected_total_published: published.length === 11589,
  expected_total_stats: stats.total_items === 11589,
  expected_total_public_stats: publicStats.total_items === 11589,
  no_arabialawer_records_main: main.filter(isTarget).length === 0,
  no_arabialawer_records_published: published.filter(isTarget).length === 0,
  no_prefixed_ids_main: main.every((item) => !String(item.id ?? '').toLowerCase().startsWith('arabialawer_')),
  no_prefixed_ids_published: published.every((item) => !String(item.id ?? '').toLowerCase().startsWith('arabialawer_')),
  no_duplicate_ids_main: duplicates(main).length === 0,
  no_duplicate_ids_published: duplicates(published).length === 0,
  main_and_published_id_sets_match: idMismatches.length === 0,
  no_missing_required_fields: missingRequired.length === 0,
};

console.log(JSON.stringify({
  checks,
  main_count: main.length,
  published_count: published.length,
  matches_main: main.filter(isTarget).length,
  matches_published: published.filter(isTarget).length,
  prefixed_ids_main: main.filter((item) => String(item.id ?? '').toLowerCase().startsWith('arabialawer_')).length,
  id_mismatches: idMismatches,
  duplicate_ids_main: duplicates(main),
  missing_required_fields: missingRequired.slice(0, 20).map((item) => ({ id: item.id, title: item.title })),
  passed: Object.values(checks).every(Boolean),
}, null, 2));
if (!Object.values(checks).every(Boolean)) process.exitCode = 1;
