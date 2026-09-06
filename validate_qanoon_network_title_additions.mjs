import fs from 'node:fs';
import path from 'node:path';

const root = '/home/ubuntu/makanez-qadaa';
const normalize = (value = '') => String(value)
  .normalize('NFKD')
  .replace(/[\u064B-\u065F\u0670\u0640]/g, '')
  .replace(/[أإآٱ]/g, 'ا')
  .replace(/ى/g, 'ي')
  .replace(/ة/g, 'ه')
  .replace(/[\p{P}\p{S}\s_]/gu, '')
  .toLowerCase();
const readItems = (file) => {
  const data = JSON.parse(fs.readFileSync(path.join(root, file), 'utf8'));
  return Array.isArray(data) ? data : data.items;
};
const items = readItems('items.json');
const publicItems = readItems('client/public/items.json');
const stats = JSON.parse(fs.readFileSync(path.join(root, 'stats.json'), 'utf8'));
const publicStats = JSON.parse(fs.readFileSync(path.join(root, 'client/public/stats.json'), 'utf8'));
const ids = new Set();
const duplicateIds = [];
for (const item of items) { if (ids.has(item.id)) duplicateIds.push(item.id); ids.add(item.id); }
const newItems = items.filter((item) => String(item.id || '').startsWith('qanoon_'));
const titleKeys = new Set();
const duplicateNewTitles = [];
for (const item of newItems) { const key = normalize(item.title); if (titleKeys.has(key)) duplicateNewTitles.push(item.title); titleKeys.add(key); }
const directLinkViolations = newItems.filter((item) => item.link_direct || item.link_telegram || item.link_drive || Number(item.download_links_count || 0) !== 0);
const sourceCounts = Object.fromEntries([...newItems.reduce((map, item) => { map.set(item.source, (map.get(item.source) || 0) + 1); return map; }, new Map())]);
const result = {
  total_items: items.length,
  public_item_count: publicItems.length,
  total_match: items.length === publicItems.length,
  stats_match: JSON.stringify(stats) === JSON.stringify(publicStats),
  stats_total_match: stats.total_items === items.length,
  duplicate_ids: duplicateIds,
  new_item_count: newItems.length,
  source_counts: sourceCounts,
  expected_source_counts_match: sourceCounts['شبكة قانونيون'] === 464 && sourceCounts['شبكة قانونيون - الرسائل والأطاريح'] === 81,
  duplicate_new_titles: duplicateNewTitles,
  direct_link_violations: directLinkViolations.map((item) => item.id),
};
result.ok = result.total_match && result.stats_match && result.stats_total_match && duplicateIds.length === 0 && result.new_item_count === 545 && result.expected_source_counts_match && duplicateNewTitles.length === 0 && directLinkViolations.length === 0;
fs.writeFileSync(path.join(root, 'qanoon_network_title_additions_post_validation.json'), JSON.stringify(result, null, 2));
console.log(JSON.stringify(result, null, 2));
if (!result.ok) process.exit(1);
