import fs from 'node:fs';
import path from 'node:path';

const root = '/home/ubuntu/makanez-qadaa';
const unwrap = (data) => Array.isArray(data) ? data : data.items;
const normalize = (value = '') => String(value).normalize('NFKD').replace(/[\u064B-\u065F\u0670\u0640]/g, '').replace(/[أإآٱ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه').replace(/[\p{P}\p{S}\s_]/gu, '').toLowerCase();
const items = unwrap(JSON.parse(fs.readFileSync(path.join(root, 'items.json'), 'utf8')));
const publicItems = unwrap(JSON.parse(fs.readFileSync(path.join(root, 'client/public/items.json'), 'utf8')));
const stats = JSON.parse(fs.readFileSync(path.join(root, 'stats.json'), 'utf8'));
const publicStats = JSON.parse(fs.readFileSync(path.join(root, 'client/public/stats.json'), 'utf8'));
const idSet = new Set();
const duplicateIds = [];
for (const item of items) { if (idSet.has(item.id)) duplicateIds.push(item.id); idSet.add(item.id); }
const prefixes = ['qanoon_theses_', 'qanoon_network_', 'nomass_title_', 'suwaid_title_'];
const added = items.filter((item) => prefixes.some((prefix) => String(item.id || '').startsWith(prefix)));
const titleKeys = new Map();
const duplicateTitles = [];
for (const item of added) { const key = normalize(item.title); if (titleKeys.has(key)) duplicateTitles.push({ first: titleKeys.get(key), duplicate: item.id, title: item.title }); else titleKeys.set(key, item.id); }
const bySource = Object.fromEntries([...added.reduce((map, item) => { map.set(item.source, (map.get(item.source) || 0) + 1); return map; }, new Map()).entries()]);
const linkViolations = added.filter((item) => item.link_direct || item.link_drive || item.link_telegram || Number(item.download_links_count || 0) !== 0).map((item) => item.id);
const invalidKinds = added.filter((item) => item.file_type !== 'عنوان').map((item) => ({ id: item.id, file_type: item.file_type }));
const result = {
  total_items: items.length,
  public_item_count: publicItems.length,
  total_matches_public: items.length === publicItems.length,
  stats_match: JSON.stringify(stats) === JSON.stringify(publicStats),
  stats_total_match: stats.total_items === items.length,
  duplicate_ids: duplicateIds,
  title_reference_count: added.length,
  source_counts: bySource,
  expected_source_counts_match: bySource['شبكة قانونيون'] === 464 && bySource['شبكة قانونيون - الرسائل والأطاريح'] === 81 && bySource['شركة نوماس للمحاماة'] === 257 && bySource['شركة السويد للمحاماة والاستشارات القانونية'] === 847,
  title_duplicates_across_new_batches: duplicateTitles,
  direct_link_violations: linkViolations,
  invalid_file_kinds: invalidKinds,
};
result.ok = result.total_matches_public && result.stats_match && result.stats_total_match && duplicateIds.length === 0 && added.length === 1649 && result.expected_source_counts_match && duplicateTitles.length === 0 && linkViolations.length === 0 && invalidKinds.length === 0;
fs.writeFileSync(path.join(root, 'channel_title_batches_latest_post_validation.json'), JSON.stringify(result, null, 2));
console.log(JSON.stringify(result, null, 2));
if (!result.ok) process.exit(1);
