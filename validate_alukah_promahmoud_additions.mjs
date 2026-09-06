import fs from 'node:fs/promises';
import crypto from 'node:crypto';

const root = process.cwd();
const mainRaw = await fs.readFile(`${root}/items.json`, 'utf8');
const publicRaw = await fs.readFile(`${root}/client/public/items.json`, 'utf8');
const mainData = JSON.parse(mainRaw);
const publicData = JSON.parse(publicRaw);
const items = Array.isArray(mainData) ? mainData : mainData.items;
const publicItems = Array.isArray(publicData) ? publicData : publicData.items;
const stats = JSON.parse(await fs.readFile(`${root}/stats.json`, 'utf8'));
const publicStats = JSON.parse(await fs.readFile(`${root}/client/public/stats.json`, 'utf8'));
const idSet = new Set();
const duplicateIds = [];
for (const item of items) {
  if (idSet.has(item.id)) duplicateIds.push(item.id);
  idSet.add(item.id);
}
const alukah = items.filter(item => item.id?.startsWith('alukah_khunayn_'));
const promahmoud = items.filter(item => item.id?.startsWith('promahmoud_'));
const hash = value => crypto.createHash('sha256').update(value).digest('hex');
const result = {
  generated_at: new Date().toISOString(),
  total_items: items.length,
  public_total_items: publicItems.length,
  main_public_hash_match: hash(mainRaw) === hash(publicRaw),
  stats_public_hash_match: hash(JSON.stringify(stats)) === hash(JSON.stringify(publicStats)),
  stats_total_match: stats.total_items === items.length && publicStats.total_items === publicItems.length,
  duplicate_ids: duplicateIds,
  alukah_count: alukah.length,
  alukah_all_accessible: alukah.every(item => item.source === 'شبكة الألوكة' && item.download_links_count === 1 && item.link_direct),
  promahmoud_count: promahmoud.length,
  promahmoud_all_accessible: promahmoud.every(item => item.source === 'موقع الأستاذ محمود' && item.download_links_count === 1 && item.link_direct),
};
const passed = result.main_public_hash_match && result.stats_public_hash_match && result.stats_total_match && duplicateIds.length === 0 && result.alukah_count === 68 && result.promahmoud_count === 13 && result.alukah_all_accessible && result.promahmoud_all_accessible;
result.passed = passed;
await fs.writeFile(`${root}/alukah_promahmoud_post_validation.json`, JSON.stringify(result, null, 2));
await fs.writeFile(`${root}/alukah_promahmoud_post_validation.txt`, Object.entries(result).map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`).join('\n'));
console.log(JSON.stringify(result));
if (!passed) process.exitCode = 1;
