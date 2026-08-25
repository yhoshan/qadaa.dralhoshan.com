import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const load = (file) => JSON.parse(readFileSync(path.join(root, file), 'utf8'));
const unwrap = (raw) => Array.isArray(raw) ? raw : raw.items;
const hash = (file) => createHash('sha256').update(readFileSync(path.join(root, file))).digest('hex');
const mainRaw = load('items.json');
const publishedRaw = load('client/public/items.json');
const stats = load('stats.json');
const statsPublished = load('client/public/stats.json');
const manifest = load('iirmll_9_duplicate_removal_manifest.json');
const main = unwrap(mainRaw);
const published = unwrap(publishedRaw);
const mainIds = main.map((item) => item.id);
const publishedIds = published.map((item) => item.id);
const iirmll = main.filter((item) => item.source === manifest.source && String(item.link_telegram ?? '').includes(manifest.required_telegram_fragment));
const report = {
  total_main: main.length,
  total_published: published.length,
  expected_total: manifest.expected.total_after,
  iirmll_count: iirmll.length,
  expected_iirmll_count: manifest.expected.source_after,
  removed_ids_remaining_main: manifest.removal_ids.filter((id) => mainIds.includes(id)),
  removed_ids_remaining_published: manifest.removal_ids.filter((id) => publishedIds.includes(id)),
  protected_ids_missing_main: manifest.protected_ids.filter((id) => !mainIds.includes(id)),
  protected_ids_missing_published: manifest.protected_ids.filter((id) => !publishedIds.includes(id)),
  protected_12629_present_main: mainIds.includes('legal_lib_12629'),
  protected_12629_present_published: publishedIds.includes('legal_lib_12629'),
  no_duplicate_ids_main: new Set(mainIds).size === mainIds.length,
  no_duplicate_ids_published: new Set(publishedIds).size === publishedIds.length,
  primary_published_same_ids: mainIds.length === publishedIds.length && mainIds.every((id, index) => id === publishedIds[index]),
  stats_total_matches: stats.total_items === main.length && statsPublished.total_items === main.length,
  stats_source_matches: stats.sources?.[manifest.source] === iirmll.length && statsPublished.sources?.[manifest.source] === iirmll.length,
  stats_files_match: JSON.stringify(stats) === JSON.stringify(statsPublished),
  hashes: {
    items_main: hash('items.json'), items_published: hash('client/public/items.json'),
    stats_main: hash('stats.json'), stats_published: hash('client/public/stats.json'),
  },
};
report.passed = report.total_main === report.expected_total && report.total_published === report.expected_total && report.iirmll_count === report.expected_iirmll_count && report.removed_ids_remaining_main.length === 0 && report.removed_ids_remaining_published.length === 0 && report.protected_ids_missing_main.length === 0 && report.protected_ids_missing_published.length === 0 && report.protected_12629_present_main && report.protected_12629_present_published && report.no_duplicate_ids_main && report.no_duplicate_ids_published && report.primary_published_same_ids && report.stats_total_matches && report.stats_source_matches && report.stats_files_match && report.hashes.items_main === report.hashes.items_published && report.hashes.stats_main === report.hashes.stats_published;
writeFileSync(path.join(root, 'iirmll_9_duplicate_removal_post_validation.json'), `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify(report, null, 2));
if (!report.passed) process.exit(1);
