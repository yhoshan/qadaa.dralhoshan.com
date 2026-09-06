import fs from 'node:fs/promises';
import crypto from 'node:crypto';

const root = process.cwd();
const [mainItemsText, publicItemsText, mainStatsText, publicStatsText, heroText, filterText, homeText, hookText] = await Promise.all([
  fs.readFile(`${root}/items.json`, 'utf8'),
  fs.readFile(`${root}/client/public/items.json`, 'utf8'),
  fs.readFile(`${root}/stats.json`, 'utf8'),
  fs.readFile(`${root}/client/public/stats.json`, 'utf8'),
  fs.readFile(`${root}/client/src/components/HeroSection.tsx`, 'utf8'),
  fs.readFile(`${root}/client/src/components/FilterBar.tsx`, 'utf8'),
  fs.readFile(`${root}/client/src/pages/Home.tsx`, 'utf8'),
  fs.readFile(`${root}/client/src/hooks/useItems.ts`, 'utf8'),
]);
const mainContainer = JSON.parse(mainItemsText);
const publicContainer = JSON.parse(publicItemsText);
const items = Array.isArray(mainContainer) ? mainContainer : mainContainer.items;
const mainStats = JSON.parse(mainStatsText);
const publicStats = JSON.parse(publicStatsText);
const hash = (text) => crypto.createHash('sha256').update(text).digest('hex');
const checks = {
  items_files_match: mainItemsText === publicItemsText,
  stats_files_match: mainStatsText === publicStatsText,
  hero_total_matches_data: mainStats.total_items === items.length,
  hero_counts_exist: ['qadaa_count', 'nizam_count', 'mohama_count'].every((key) => Number.isInteger(mainStats[key]) && mainStats[key] >= 0),
  hero_counts_sum_to_total: mainStats.qadaa_count + mainStats.nizam_count + mainStats.mohama_count === mainStats.total_items,
  hero_uses_actual_counts: !heroText.includes('qadaa_count?.toLocaleString("en-US") ?? "..."') && heroText.includes('stats?.qadaa_count?.toLocaleString("en-US")'),
  no_file_or_source_props_in_filterbar: !/fileTypes|sources/.test(filterText),
  no_file_or_source_props_passed_from_home: !/fileTypes=|sources=/.test(homeText),
  cache_buster_updated: hookText.includes('hero-stats-filter-controls-2026-09-06') && !hookText.includes('marqoom-sadr-open-links-2026-09-06'),
};
const report = {
  checked_at: new Date().toISOString(),
  counts: { total_items: mainStats.total_items, qadaa_count: mainStats.qadaa_count, nizam_count: mainStats.nizam_count, mohama_count: mainStats.mohama_count },
  hashes: { items: hash(mainItemsText), stats: hash(mainStatsText) },
  checks,
  success: Object.values(checks).every(Boolean),
};
await fs.writeFile(`${root}/hero_stats_filters_validation.json`, JSON.stringify(report, null, 2));
await fs.writeFile(`${root}/hero_stats_filters_validation.txt`, [
  `نجح الفحص: ${report.success ? 'نعم' : 'لا'}`,
  `إجمالي المواد: ${report.counts.total_items.toLocaleString('en-US')}`,
  `القضاء: ${report.counts.qadaa_count.toLocaleString('en-US')}`,
  `الأنظمة: ${report.counts.nizam_count.toLocaleString('en-US')}`,
  `المحاماة: ${report.counts.mohama_count.toLocaleString('en-US')}`,
  '',
  ...Object.entries(checks).map(([name, passed]) => `${passed ? '[PASS]' : '[FAIL]'} ${name}`),
].join('\n'));
console.log(JSON.stringify(report));
if (!report.success) process.exitCode = 1;
