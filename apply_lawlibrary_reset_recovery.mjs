import { readFile, writeFile } from 'node:fs/promises';

const root = process.cwd();
const unwrap = (raw) => Array.isArray(raw) ? raw : raw.items;
const rewrap = (raw, items) => Array.isArray(raw) ? items : { ...raw, items };
const normalizeTitle = (value = '') => String(value)
  .normalize('NFKD')
  .replace(/[\u064B-\u065F\u0670]/g, '')
  .replace(/[أإآٱ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي')
  .replace(/[\u200e\u200f\u202a-\u202e\u2066-\u2069]/g, '')
  .toLowerCase().replace(/[^\p{L}\p{N}]/gu, '');
const normalizeUrl = (value = '') => String(value).trim().replace(/#.*$/, '').replace(/\/$/, '').toLowerCase();
const countBy = (rows, field) => Object.fromEntries([...rows.reduce((map, row) => { const key = row[field] || 'غير محدد'; map.set(key, (map.get(key) || 0) + 1); return map; }, new Map()).entries()].sort((a, b) => b[1] - a[1]));
const categoryBucket = (category = '') => {
  if (category === 'الأنظمة والتشريعات') return 'nizam';
  if (category.includes('المحاماة')) return 'mohama';
  if (/قضاء|محكم|إثبات|جنايات|حسبة|إجراءات|مبادئ|قضايا/.test(category)) return 'qadaa';
  return 'other';
};

const rawItems = JSON.parse(await readFile(`${root}/items.json`, 'utf8'));
const items = unwrap(rawItems);
const rawStats = JSON.parse(await readFile(`${root}/stats.json`, 'utf8'));
const manifest = JSON.parse(await readFile(`${root}/lawlibrary_recovery_accessible_manifest.json`, 'utf8'));
const titleKeys = new Set(items.map((item) => normalizeTitle(item.title)).filter(Boolean));
const urlKeys = new Set(items.map((item) => normalizeUrl(item.link_direct || item.link_drive || item.link_telegram)).filter(Boolean));
const usedIds = new Set(items.map((item) => item.id));
const maxSequence = Math.max(0, ...items.map((item) => /^lawlibrary_(\d+)$/.exec(item.id || '')).filter(Boolean).map((match) => Number(match[1])));
let nextSequence = maxSequence + 1;
const restored = []; const skipped = [];
for (const candidate of manifest.selected) {
  const titleKey = normalizeTitle(candidate.title);
  const urlKey = normalizeUrl(candidate.link_direct || candidate.link_drive || candidate.link_telegram);
  if (!titleKey || !urlKey || titleKeys.has(titleKey) || urlKeys.has(urlKey)) { skipped.push({ input_id: candidate.id, title: candidate.title, reason: !titleKey || !urlKey ? 'بيانات ناقصة' : 'ظهر تكرار عند التنفيذ' }); continue; }
  let id;
  do { id = `lawlibrary_${String(nextSequence++).padStart(3, '0')}`; } while (usedIds.has(id));
  const item = {
    id,
    title: candidate.title.trim(),
    author: candidate.author || '',
    investigator: candidate.investigator || '',
    publisher: candidate.publisher || candidate.source || '',
    year: candidate.year || '',
    link_telegram: candidate.link_telegram || '',
    link_drive: candidate.link_drive || '',
    link_direct: candidate.link_direct || '',
    source: 'مكتبة القانون',
    category: candidate.category || 'الأبحاث القانونية والقضائية',
    material_type: candidate.material_type || 'رابط مرجعي',
    file_type: candidate.file_type || 'رابط',
    file_size: candidate.file_size || '',
    pages_count: candidate.pages_count || '',
    is_featured: Boolean(candidate.is_featured),
    download_links_count: Number(candidate.download_links_count || [candidate.link_telegram, candidate.link_drive, candidate.link_direct].filter(Boolean).length),
  };
  restored.push({ input_id: candidate.id, item }); titleKeys.add(titleKey); urlKeys.add(urlKey); usedIds.add(id); items.push(item);
}
if (restored.length === 0) throw new Error('لم يُستعد أي سجل؛ أوقفت التنفيذ لحماية البيانات.');
const allCategories = countBy(items, 'category'); const allSources = countBy(items, 'source'); const allFileTypes = countBy(items, 'file_type');
const allBuckets = items.reduce((acc, item) => { acc[categoryBucket(item.category)] += 1; return acc; }, { qadaa: 0, nizam: 0, mohama: 0, other: 0 });
const nextStats = {
  ...rawStats,
  total_items: items.length,
  qadaa_count: allBuckets.qadaa,
  nizam_count: allBuckets.nizam,
  mohama_count: allBuckets.mohama,
  other_count: allBuckets.other,
  books_count: items.length,
  audio_count: items.filter((item) => item.file_type === 'MP3').length,
  video_count: items.filter((item) => item.file_type === 'MP4' || item.file_type === 'فيديو').length,
  categories: allCategories,
  sources: allSources,
  file_types: allFileTypes,
  featured_count: items.filter((item) => item.is_featured).length,
  with_download_links: items.filter((item) => Number(item.download_links_count || 0) > 0).length,
};
const useItemsPath = `${root}/client/src/hooks/useItems.ts`;
const useItems = await readFile(useItemsPath, 'utf8');
const cacheTag = 'lawlibrary-reset-recovery-290-2026-09-06';
const nextUseItems = useItems.replace(/items\.json\?v=[^`]+/g, `items.json?v=${cacheTag}`).replace(/stats\.json\?v=[^`]+/g, `stats.json?v=${cacheTag}`);
await writeFile(`${root}/items.json`, `${JSON.stringify(rewrap(rawItems, items), null, 2)}\n`);
await writeFile(`${root}/client/public/items.json`, `${JSON.stringify(rewrap(rawItems, items), null, 2)}\n`);
await writeFile(`${root}/stats.json`, `${JSON.stringify(nextStats, null, 2)}\n`);
await writeFile(`${root}/client/public/stats.json`, `${JSON.stringify(nextStats, null, 2)}\n`);
await writeFile(useItemsPath, nextUseItems);
const execution = { executed_at: new Date().toISOString(), previous_total: items.length - restored.length, restored_count: restored.length, skipped_at_execution: skipped.length, next_total: items.length, lawlibrary_count: allSources['مكتبة القانون'] || 0, first_id: restored[0].item.id, last_id: restored.at(-1).item.id, cache_tag: cacheTag, restored, skipped };
await writeFile(`${root}/lawlibrary_reset_recovery_execution.json`, `${JSON.stringify(execution, null, 2)}\n`);
console.log(JSON.stringify({ previous_total: execution.previous_total, restored: execution.restored_count, skipped: execution.skipped_at_execution, next_total: execution.next_total, lawlibrary_count: execution.lawlibrary_count, ids: `${execution.first_id}–${execution.last_id}` }, null, 2));
