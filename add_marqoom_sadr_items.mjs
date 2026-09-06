import fs from 'node:fs/promises';

const root = process.cwd();
const mainItemsPath = `${root}/items.json`;
const publicItemsPath = `${root}/client/public/items.json`;
const mainStatsPath = `${root}/stats.json`;
const publicStatsPath = `${root}/client/public/stats.json`;
const cachePath = `${root}/client/src/hooks/useItems.ts`;
const preflight = JSON.parse(await fs.readFile(`${root}/marqoom_sadr_additions_preflight.json`, 'utf8'));
const rawItems = JSON.parse(await fs.readFile(mainItemsPath, 'utf8'));
const rawStats = JSON.parse(await fs.readFile(mainStatsPath, 'utf8'));
const items = Array.isArray(rawItems) ? rawItems : rawItems.items;

function normalizeArabic(value = '') {
  return String(value).normalize('NFKD').replace(/[\u064B-\u065F\u0670\u0640]/g, '').replace(/[أإآٱ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه').replace(/ؤ/g, 'و').replace(/ئ/g, 'ي').replace(/[^\p{L}\p{N}]+/gu, '').toLowerCase();
}
function normalizeUrl(value = '') { return String(value).trim().replace(/^http:\/\//iu, 'https://').replace(/[?&]key=\d+$/u, '').replace(/\/$/u, ''); }
function nextId(prefix, used) {
  let serial = 1;
  while (used.has(`${prefix}_${String(serial).padStart(3, '0')}`)) serial += 1;
  const id = `${prefix}_${String(serial).padStart(3, '0')}`;
  used.add(id);
  return id;
}
function sortCounts(counts) {
  return Object.fromEntries(Object.entries(counts).sort(([nameA, countA], [nameB, countB]) => countB - countA || nameA.localeCompare(nameB, 'ar')));
}
function countBy(list, field) {
  return sortCounts(list.reduce((counts, item) => {
    const value = item[field] || '';
    if (value) counts[value] = (counts[value] || 0) + 1;
    return counts;
  }, {}));
}

if (!Array.isArray(items)) throw new Error('بنية items.json غير متوقعة');
if (preflight.current_total !== items.length) throw new Error(`تغيرت قاعدة البيانات منذ الفحص النهائي: المتوقع ${preflight.current_total} والحالي ${items.length}`);
if (preflight.accepted_total !== 61 || preflight.rejected_total !== 0) throw new Error('نتيجة الفحص النهائي لا تطابق دفعة الإضافة المعتمدة');

const existingIds = new Set(items.map((item) => item.id));
const existingTitles = new Set(items.map((item) => normalizeArabic(item.title)));
const existingUrls = new Set(items.flatMap((item) => [item.link_direct, item.link_drive, item.link_telegram]).filter(Boolean).map(normalizeUrl));
const additions = [];
for (const candidate of preflight.accepted) {
  const titleKey = normalizeArabic(candidate.title);
  const urlKey = normalizeUrl(candidate.link_direct);
  if (existingTitles.has(titleKey)) throw new Error(`تكرار عنوان قبل الإضافة: ${candidate.title}`);
  if (existingUrls.has(urlKey)) throw new Error(`تكرار رابط قبل الإضافة: ${candidate.link_direct}`);
  const prefix = candidate.source === 'شبكة مكتبة القانون' ? 'marqoom' : 'sadr';
  const item = {
    id: nextId(prefix, existingIds),
    title: candidate.title,
    author: candidate.author || '',
    investigator: candidate.investigator || '',
    publisher: candidate.publisher || candidate.source,
    year: candidate.year || '',
    link_telegram: '',
    link_drive: '',
    link_direct: candidate.link_direct,
    source: candidate.source,
    category: candidate.category,
    material_type: candidate.material_type,
    file_type: candidate.file_type,
    file_size: candidate.file_size || '',
    pages_count: candidate.pages_count || '',
    is_featured: false,
    download_links_count: 1,
  };
  additions.push(item);
  existingTitles.add(titleKey);
  existingUrls.add(urlKey);
}
const updatedItems = [...items, ...additions];
const nextStats = {
  ...rawStats,
  total_items: updatedItems.length,
  categories: countBy(updatedItems, 'category'),
  sources: countBy(updatedItems, 'source'),
  material_types: countBy(updatedItems, 'material_type'),
  file_types: countBy(updatedItems, 'file_type'),
  featured_count: updatedItems.filter((item) => item.is_featured).length,
  with_download_links: updatedItems.filter((item) => Number(item.download_links_count || 0) > 0).length,
};
const updatedItemsContainer = Array.isArray(rawItems) ? updatedItems : { ...rawItems, items: updatedItems };
const cache = await fs.readFile(cachePath, 'utf8');
const updatedCache = cache.replaceAll('promahmoud-source-reference-2026-09-06', 'marqoom-sadr-open-links-2026-09-06');
if (updatedCache === cache) throw new Error('لم تُعثر معلمة كسر الكاش الحالية');

await fs.writeFile(mainItemsPath, JSON.stringify(updatedItemsContainer, null, 2) + '\n');
await fs.writeFile(publicItemsPath, JSON.stringify(updatedItemsContainer, null, 2) + '\n');
await fs.writeFile(mainStatsPath, JSON.stringify(nextStats, null, 2) + '\n');
await fs.writeFile(publicStatsPath, JSON.stringify(nextStats, null, 2) + '\n');
await fs.writeFile(cachePath, updatedCache);

const sourceCounts = countBy(additions, 'source');
const execution = {
  executed_at: new Date().toISOString(),
  before_total: items.length,
  added_total: additions.length,
  after_total: updatedItems.length,
  by_source: sourceCounts,
  items: additions.map((item) => ({ id: item.id, title: item.title, source: item.source, category: item.category, material_type: item.material_type, link_direct: item.link_direct })),
};
await fs.writeFile(`${root}/marqoom_sadr_additions_execution.json`, JSON.stringify(execution, null, 2));
console.log(JSON.stringify({ before_total: execution.before_total, added_total: execution.added_total, after_total: execution.after_total, by_source: execution.by_source }));
