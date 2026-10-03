import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const paths = {
  items: path.join(root, 'items.json'),
  publicItems: path.join(root, 'client/public/items.json'),
  stats: path.join(root, 'stats.json'),
  publicStats: path.join(root, 'client/public/stats.json'),
  cache: path.join(root, 'client/src/hooks/useItems.ts'),
  candidates: path.join(root, 'jtc_qiyam_2026-10-03_candidates.json'),
};
const backupDir = path.join(root, 'backups/jtc_qiyam_2026-10-03');
const executionPath = path.join(root, 'jtc_qiyam_2026-10-03_execution.json');
const expectedBefore = 20069;
const expectedAdditions = 11;
const currentCacheToken = 'qadaa-moj-portal-catalogues-2026-10-03';
const nextCacheToken = 'qadaa-jtc-qiyam-2026-10-03';

function sha256(value) { return crypto.createHash('sha256').update(value).digest('hex'); }
function normalizeArabic(value = '') {
  return String(value).normalize('NFKD')
    .replace(/[\u064B-\u065F\u0670\u0640]/g, '')
    .replace(/[أإآٱ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه').replace(/ؤ/g, 'و').replace(/ئ/g, 'ي')
    .replace(/[^\p{L}\p{N}]+/gu, '').toLowerCase();
}
function normalizeUrl(value = '') { return String(value).trim().replace(/^http:\/\//iu, 'https://').replace(/\/$/u, ''); }
function unwrap(value) {
  const items = Array.isArray(value) ? value : value?.items;
  if (!Array.isArray(items)) throw new Error('بنية ملف المواد غير متوقعة');
  return items;
}
function rewrap(value, items) { return Array.isArray(value) ? items : { ...value, items }; }
function countBy(items, key) {
  const counts = {};
  for (const item of items) {
    const value = String(item[key] || '').trim();
    if (value) counts[value] = (counts[value] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).sort(([a, ac], [b, bc]) => bc - ac || a.localeCompare(b, 'ar')));
}

const [itemsText, publicItemsText, statsText, publicStatsText, cacheText, candidatesText] = await Promise.all(Object.values(paths).map((file) => fs.readFile(file, 'utf8')));
if (itemsText !== publicItemsText) throw new Error('ملفا المواد الرئيس والمنشور غير متطابقين قبل الإضافة');
if (statsText !== publicStatsText) throw new Error('ملفا الإحصاءات الرئيس والمنشور غير متطابقين قبل الإضافة');
if (!cacheText.includes(currentCacheToken)) throw new Error('معلمة كسر الكاش السابقة غير موجودة');
const mainContainer = JSON.parse(itemsText);
const publicContainer = JSON.parse(publicItemsText);
const currentItems = unwrap(mainContainer);
unwrap(publicContainer);
const currentStats = JSON.parse(statsText);
const candidates = JSON.parse(candidatesText);
if (currentItems.length !== expectedBefore) throw new Error(`الإجمالي السابق غير متوقع: ${currentItems.length} بدلاً من ${expectedBefore}`);
if (!Array.isArray(candidates) || candidates.length !== expectedAdditions) throw new Error('عدد مرشحي المصدرين غير صحيح');
if (await fs.stat(backupDir).then(() => true).catch(() => false)) throw new Error(`مسار النسخة الاحتياطية موجود: ${backupDir}`);

const ids = new Set(currentItems.map((item) => String(item.id)));
const titles = new Set(currentItems.map((item) => normalizeArabic(item.title)));
const exactRecords = new Set(currentItems.map((item) => `${normalizeArabic(item.title)}\u0000${normalizeUrl(item.link_direct)}`));
const candidateIds = new Set(), candidateTitles = new Set(), candidateRecords = new Set();
for (const item of candidates) {
  for (const field of ['id', 'title', 'link_direct', 'source', 'category', 'material_type', 'file_type']) if (!item[field]) throw new Error(`حقل مطلوب مفقود: ${field}`);
  if (!/^(jtc|qiyam)_[a-z0-9_]+$/u.test(item.id)) throw new Error(`بادئة معرّف غير معتمدة: ${item.id}`);
  const title = normalizeArabic(item.title), url = normalizeUrl(item.link_direct), record = `${title}\u0000${url}`;
  if (ids.has(item.id) || candidateIds.has(item.id)) throw new Error(`تكرار معرّف: ${item.id}`);
  if (titles.has(title) || candidateTitles.has(title)) throw new Error(`تكرار عنوان: ${item.title}`);
  if (exactRecords.has(record) || candidateRecords.has(record)) throw new Error(`تكرار سجل مرجعي: ${item.title}`);
  candidateIds.add(item.id); candidateTitles.add(title); candidateRecords.add(record);
}

await fs.mkdir(backupDir, { recursive: true });
const backupFiles = {
  'items.before.json': itemsText,
  'client-public-items.before.json': publicItemsText,
  'stats.before.json': statsText,
  'client-public-stats.before.json': publicStatsText,
  'useItems.before.ts': cacheText,
  'candidates.json': candidatesText,
};
await Promise.all(Object.entries(backupFiles).map(([name, data]) => fs.writeFile(path.join(backupDir, name), data)));
await fs.writeFile(path.join(backupDir, 'manifest.json'), JSON.stringify({
  created_at: new Date().toISOString(),
  purpose: 'نسخة احتياطية قبل إضافة مواد عامة غير مكررة من مركز التدريب العدلي ومكتبة قيم للقانون',
  before_total: currentItems.length,
  expected_additions: expectedAdditions,
  files: Object.fromEntries(Object.entries(backupFiles).map(([name, data]) => [name, sha256(data)])),
}, null, 2) + '\n');

const updatedItems = [...currentItems, ...candidates];
const updatedStats = {
  ...currentStats,
  total_items: updatedItems.length,
  categories: countBy(updatedItems, 'category'),
  sources: countBy(updatedItems, 'source'),
  material_types: countBy(updatedItems, 'material_type'),
  file_types: countBy(updatedItems, 'file_type'),
  featured_count: updatedItems.filter((item) => item.is_featured).length,
  with_download_links: updatedItems.filter((item) => Number(item.download_links_count || 0) > 0).length,
};
await Promise.all([
  fs.writeFile(paths.items, JSON.stringify(rewrap(mainContainer, updatedItems), null, 2) + '\n'),
  fs.writeFile(paths.publicItems, JSON.stringify(rewrap(publicContainer, updatedItems), null, 2) + '\n'),
  fs.writeFile(paths.stats, JSON.stringify(updatedStats, null, 2) + '\n'),
  fs.writeFile(paths.publicStats, JSON.stringify(updatedStats, null, 2) + '\n'),
  fs.writeFile(paths.cache, cacheText.replaceAll(currentCacheToken, nextCacheToken)),
]);
const bySource = Object.fromEntries(Object.entries(countBy(candidates, 'source')));
const execution = { executed_at: new Date().toISOString(), before_total: currentItems.length, added_total: candidates.length, after_total: updatedItems.length, backup_directory: path.relative(root, backupDir), cache_buster: nextCacheToken, added_by_source: bySource, added_ids: candidates.map((item) => item.id) };
await fs.writeFile(executionPath, JSON.stringify(execution, null, 2) + '\n');
console.log(JSON.stringify(execution, null, 2));
