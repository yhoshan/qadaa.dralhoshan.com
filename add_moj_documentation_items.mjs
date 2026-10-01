import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const mainItemsPath = path.join(root, 'items.json');
const publicItemsPath = path.join(root, 'client/public/items.json');
const mainStatsPath = path.join(root, 'stats.json');
const publicStatsPath = path.join(root, 'client/public/stats.json');
const cachePath = path.join(root, 'client/src/hooks/useItems.ts');
const candidatesPath = path.join(root, 'moj_documentation_2026-09-28_candidates.json');
const backupDir = path.join(root, 'backups/moj_documentation_2026-09-28');
const sourceName = 'وزارة العدل السعودية — البوابة القانونية';
const expectedBeforeTotal = 17172;

function sha256(value) {
  return crypto.createHash('sha256').update(value).digest('hex');
}
function normalizeArabic(value = '') {
  return String(value)
    .normalize('NFKD')
    .replace(/[\u064B-\u065F\u0670\u0640]/g, '')
    .replace(/[أإآٱ]/g, 'ا')
    .replace(/ى/g, 'ي')
    .replace(/ة/g, 'ه')
    .replace(/ؤ/g, 'و')
    .replace(/ئ/g, 'ي')
    .replace(/[^\p{L}\p{N}]+/gu, '')
    .toLowerCase();
}
function normalizeUrl(value = '') {
  return String(value).trim().replace(/^http:\/\//iu, 'https://').replace(/\/$/u, '');
}
function countBy(list, field) {
  const counts = list.reduce((acc, item) => {
    const value = item[field] || '';
    if (value) acc[value] = (acc[value] || 0) + 1;
    return acc;
  }, {});
  return Object.fromEntries(Object.entries(counts).sort(([a, aCount], [b, bCount]) => bCount - aCount || a.localeCompare(b, 'ar')));
}
function extractItems(container) {
  const records = Array.isArray(container) ? container : container?.items;
  if (!Array.isArray(records)) throw new Error('بنية items.json غير متوقعة');
  return records;
}
function rewrap(container, records) {
  return Array.isArray(container) ? records : { ...container, items: records };
}

const [mainText, publicText, mainStatsText, publicStatsText, cache, candidatesText] = await Promise.all([
  fs.readFile(mainItemsPath, 'utf8'),
  fs.readFile(publicItemsPath, 'utf8'),
  fs.readFile(mainStatsPath, 'utf8'),
  fs.readFile(publicStatsPath, 'utf8'),
  fs.readFile(cachePath, 'utf8'),
  fs.readFile(candidatesPath, 'utf8'),
]);

if (mainText !== publicText) throw new Error('النسخة الرئيسية والمنشورة للمواد غير متطابقتين قبل الإضافة');
if (mainStatsText !== publicStatsText) throw new Error('النسخة الرئيسية والمنشورة للإحصاءات غير متطابقتين قبل الإضافة');
const mainContainer = JSON.parse(mainText);
const publicContainer = JSON.parse(publicText);
const mainStats = JSON.parse(mainStatsText);
const candidates = JSON.parse(candidatesText);
const items = extractItems(mainContainer);
extractItems(publicContainer);
if (items.length !== expectedBeforeTotal) throw new Error(`إجمالي سابق غير متوقع: ${items.length} بدلاً من ${expectedBeforeTotal}`);
if (!Array.isArray(candidates) || candidates.length !== 6) throw new Error('دفعة وزارة العدل يجب أن تحتوي ست مواد فقط');
if (items.some((item) => item.source === sourceName || String(item.id).startsWith('moj_docs_'))) throw new Error('توجد إضافة سابقة من المصدر الرسمي أو معرّفات الدفعة');

const ids = new Set(items.map((item) => item.id));
const titles = new Set(items.map((item) => normalizeArabic(item.title)));
const urls = new Set(items.flatMap((item) => [item.link_direct, item.link_drive, item.link_telegram]).filter(Boolean).map(normalizeUrl));
const candidateIds = new Set();
const candidateTitles = new Set();
const candidateUrls = new Set();
for (const candidate of candidates) {
  const required = ['id', 'title', 'link_direct', 'source', 'category', 'material_type', 'file_type'];
  for (const field of required) if (!candidate[field]) throw new Error(`حقل مطلوب مفقود في مادة وزارة العدل: ${field}`);
  if (!candidate.id.startsWith('moj_docs_')) throw new Error(`بادئة معرّف غير معتمدة: ${candidate.id}`);
  if (candidate.source !== sourceName) throw new Error(`مصدر غير معتمد: ${candidate.source}`);
  const normalizedTitle = normalizeArabic(candidate.title);
  const normalizedUrl = normalizeUrl(candidate.link_direct);
  if (ids.has(candidate.id) || candidateIds.has(candidate.id)) throw new Error(`تكرار معرّف: ${candidate.id}`);
  if (titles.has(normalizedTitle) || candidateTitles.has(normalizedTitle)) throw new Error(`تكرار عنوان بعد التطبيع: ${candidate.title}`);
  if (urls.has(normalizedUrl) || candidateUrls.has(normalizedUrl)) throw new Error(`تكرار رابط: ${candidate.link_direct}`);
  candidateIds.add(candidate.id);
  candidateTitles.add(normalizedTitle);
  candidateUrls.add(normalizedUrl);
}

const backupManifest = {
  created_at: new Date().toISOString(),
  purpose: 'نسخة احتياطية قبل إضافة ست وثائق عدلية رسمية من البوابة القانونية لوزارة العدل السعودية',
  before_total: items.length,
  files: {
    'items.before.json': sha256(mainText),
    'client-public-items.before.json': sha256(publicText),
    'stats.before.json': sha256(mainStatsText),
    'client-public-stats.before.json': sha256(publicStatsText),
    'useItems.before.ts': sha256(cache),
  },
};
await fs.mkdir(backupDir, { recursive: true });
await Promise.all([
  fs.writeFile(path.join(backupDir, 'items.before.json'), mainText),
  fs.writeFile(path.join(backupDir, 'client-public-items.before.json'), publicText),
  fs.writeFile(path.join(backupDir, 'stats.before.json'), mainStatsText),
  fs.writeFile(path.join(backupDir, 'client-public-stats.before.json'), publicStatsText),
  fs.writeFile(path.join(backupDir, 'useItems.before.ts'), cache),
  fs.writeFile(path.join(backupDir, 'manifest.json'), JSON.stringify(backupManifest, null, 2) + '\n'),
]);

const updatedItems = [...items, ...candidates];
const updatedStats = {
  ...mainStats,
  total_items: updatedItems.length,
  categories: countBy(updatedItems, 'category'),
  sources: countBy(updatedItems, 'source'),
  material_types: countBy(updatedItems, 'material_type'),
  file_types: countBy(updatedItems, 'file_type'),
  featured_count: updatedItems.filter((item) => item.is_featured).length,
  with_download_links: updatedItems.filter((item) => Number(item.download_links_count || 0) > 0).length,
};
const previousCacheToken = 'qadaa-manifest-188-removal-2026-09-06';
const nextCacheToken = 'moj-official-documents-2026-09-28';
if (!cache.includes(previousCacheToken)) throw new Error('لم تُعثر معلمة كسر الكاش الحالية');
const updatedCache = cache.replaceAll(previousCacheToken, nextCacheToken);

await Promise.all([
  fs.writeFile(mainItemsPath, JSON.stringify(rewrap(mainContainer, updatedItems), null, 2) + '\n'),
  fs.writeFile(publicItemsPath, JSON.stringify(rewrap(publicContainer, updatedItems), null, 2) + '\n'),
  fs.writeFile(mainStatsPath, JSON.stringify(updatedStats, null, 2) + '\n'),
  fs.writeFile(publicStatsPath, JSON.stringify(updatedStats, null, 2) + '\n'),
  fs.writeFile(cachePath, updatedCache),
]);

const execution = {
  executed_at: new Date().toISOString(),
  source: sourceName,
  before_total: items.length,
  added_total: candidates.length,
  after_total: updatedItems.length,
  backup_directory: path.relative(root, backupDir),
  cache_buster: nextCacheToken,
  additions: candidates.map(({ official_serial, release_date_hijri, ...item }) => ({ ...item, official_serial, release_date_hijri })),
};
await fs.writeFile(path.join(root, 'moj_documentation_2026-09-28_execution.json'), JSON.stringify(execution, null, 2) + '\n');
console.log(JSON.stringify({ before_total: execution.before_total, added_total: execution.added_total, after_total: execution.after_total, source: execution.source, backup_directory: execution.backup_directory }));
