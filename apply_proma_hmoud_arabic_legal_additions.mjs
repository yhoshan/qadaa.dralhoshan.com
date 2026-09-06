import fs from 'node:fs/promises';

const root = process.cwd();
const itemsPath = `${root}/items.json`;
const publicItemsPath = `${root}/client/public/items.json`;
const statsPath = `${root}/stats.json`;
const publicStatsPath = `${root}/client/public/stats.json`;
const hookPath = `${root}/client/src/hooks/useItems.ts`;
const validation = JSON.parse(await fs.readFile(`${root}/promahmoud_arabic_legal_link_validation.json`, 'utf8'));
const rawData = JSON.parse(await fs.readFile(itemsPath, 'utf8'));
const items = Array.isArray(rawData) ? rawData : rawData.items;

function normalizeTitle(value = '') {
  return value
    .normalize('NFKD')
    .replace(/[\u064B-\u065F\u0670\u0640]/g, '')
    .replace(/[أإآٱ]/g, 'ا')
    .replace(/ى/g, 'ي')
    .replace(/ة/g, 'ه')
    .replace(/[^\p{L}\p{N}]+/gu, '')
    .toLowerCase();
}

const existingTitles = new Set(items.map(item => normalizeTitle(item.title ?? '')).filter(Boolean));
const existingLinks = new Set(items.flatMap(item => [item.link_direct, item.link_telegram, item.link_drive]).filter(Boolean));
const existingIds = new Set(items.map(item => item.id));
let sequence = 1;
function nextId() {
  while (existingIds.has(`promahmoud_${String(sequence).padStart(3, '0')}`)) sequence += 1;
  const id = `promahmoud_${String(sequence).padStart(3, '0')}`;
  existingIds.add(id);
  sequence += 1;
  return id;
}
function countBy(field) {
  const counts = new Map();
  for (const item of items) {
    const key = String(item[field] ?? '');
    counts.set(key, (counts.get(key) ?? 0) + 1);
  }
  return Object.fromEntries([...counts.entries()].sort((a, b) => b[1] - a[1]));
}

const additions = [];
const skipped = [];
for (const candidate of validation.accessible ?? []) {
  const key = normalizeTitle(candidate.title);
  if (existingTitles.has(key) || existingLinks.has(candidate.link_direct)) {
    skipped.push({ ...candidate, reason: existingTitles.has(key) ? 'TITLE_DUPLICATE_AT_APPLY' : 'LINK_DUPLICATE_AT_APPLY' });
    continue;
  }
  const record = {
    id: nextId(),
    title: candidate.title,
    author: candidate.author,
    investigator: '',
    publisher: candidate.publisher,
    year: '',
    link_telegram: '',
    link_drive: '',
    link_direct: candidate.link_direct,
    source: candidate.source,
    category: candidate.category,
    material_type: 'بحث',
    file_type: 'رابط',
    file_size: '',
    pages_count: '',
    is_featured: false,
    download_links_count: 1,
  };
  additions.push(record);
  items.push(record);
  existingTitles.add(key);
  existingLinks.add(candidate.link_direct);
}

const stats = {
  total_items: items.length,
  categories: countBy('category'),
  sources: countBy('source'),
  material_types: countBy('material_type'),
  file_types: countBy('file_type'),
  featured_count: items.filter(item => item.is_featured).length,
  with_download_links: items.filter(item => Number(item.download_links_count ?? 0) > 0).length,
};
const finalData = Array.isArray(rawData) ? items : { ...rawData, items };
await fs.writeFile(itemsPath, JSON.stringify(finalData, null, 2));
await fs.writeFile(publicItemsPath, JSON.stringify(finalData, null, 2));
await fs.writeFile(statsPath, JSON.stringify(stats, null, 2));
await fs.writeFile(publicStatsPath, JSON.stringify(stats, null, 2));
let hook = await fs.readFile(hookPath, 'utf8');
hook = hook.replace(/(\/items\.json\?v=)[^'"`\s)]+/g, '$1promahmoud-arabic-legal-additions-2026-09-06');
hook = hook.replace(/(\/stats\.json\?v=)[^'"`\s)]+/g, '$1promahmoud-arabic-legal-additions-2026-09-06');
await fs.writeFile(hookPath, hook);
const execution = {
  generated_at: new Date().toISOString(),
  before_total: items.length - additions.length,
  added_count: additions.length,
  skipped_at_apply: skipped.length,
  after_total: items.length,
  source_count_after: stats.sources['مكتبة الدكتور محمود لطفي عبد العزيز القانونية'] ?? 0,
  additions,
  skipped,
};
await fs.writeFile(`${root}/promahmoud_arabic_legal_additions_execution.json`, JSON.stringify(execution, null, 2));
await fs.writeFile(`${root}/promahmoud_arabic_legal_additions_manifest.txt`, [
  `إضافة المواد العربية القانونية من موقع الأستاذ محمود: ${execution.generated_at}`,
  `قبل: ${execution.before_total}`,
  `المضاف: ${execution.added_count}`,
  `المؤجل عند الإضافة: ${execution.skipped_at_apply}`,
  `بعد: ${execution.after_total}`,
  `عدد المصدر بعد الإضافة: ${execution.source_count_after}`,
  '',
  ...additions.map((item, index) => `${index + 1}. ${item.id} | ${item.title} | ${item.link_direct}`),
].join('\n'));
console.log(JSON.stringify({ before: execution.before_total, added: execution.added_count, after: execution.after_total }));
