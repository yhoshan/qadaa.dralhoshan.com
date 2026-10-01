import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const paths = {
  mainItems: path.join(root, 'items.json'),
  publicItems: path.join(root, 'client/public/items.json'),
  mainStats: path.join(root, 'stats.json'),
  publicStats: path.join(root, 'client/public/stats.json'),
  cache: path.join(root, 'client/src/hooks/useItems.ts'),
  additions: '/home/ubuntu/upload/pasted_file_rCwoBj_qadaa_add_boe_official_538.csv',
  deletions: '/home/ubuntu/upload/pasted_file_ClHru3_qadaa_remove_intermediary_226.csv',
  manifest: '/home/ubuntu/upload/pasted_file_pN8Ytn_qadaa_boe_execution_manifest.json',
  execution: path.join(root, 'boe_official_replacement_2026-09-29_execution.json'),
};
const expected = { before: 17178, additions: 538, deletions: 226, after: 17490 };
const officialSource = 'هيئة الخبراء بمجلس الوزراء';
const officialPrefix = 'https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/';
const oldCacheToken = 'moj-official-documents-2026-09-28';
const newCacheToken = 'boe-official-canonical-538-2026-09-29';

function sha256(value) {
  return crypto.createHash('sha256').update(value).digest('hex');
}
function parseCsv(text) {
  const rows = [];
  let row = [], cell = '', quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"') {
        if (text[i + 1] === '"') { cell += '"'; i += 1; }
        else quoted = false;
      } else cell += ch;
    } else if (ch === '"') quoted = true;
    else if (ch === ',') { row.push(cell); cell = ''; }
    else if (ch === '\n') { row.push(cell.replace(/\r$/u, '')); rows.push(row); row = []; cell = ''; }
    else cell += ch;
  }
  if (cell || row.length) { row.push(cell.replace(/\r$/u, '')); rows.push(row); }
  const [header, ...body] = rows;
  return body.filter((r) => r.some((v) => v !== '')).map((r) => Object.fromEntries(header.map((h, i) => [h.replace(/^\uFEFF/u, ''), r[i] ?? ''])));
}
function extractItems(container) {
  const records = Array.isArray(container) ? container : container?.items;
  if (!Array.isArray(records)) throw new Error('بنية items.json غير متوقعة');
  return records;
}
function rewrap(container, records) {
  return Array.isArray(container) ? records : { ...container, items: records };
}
function countBy(items, field) {
  const counts = {};
  for (const item of items) {
    const value = item[field] || '';
    if (value) counts[value] = (counts[value] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(counts).sort(([a, ac], [b, bc]) => bc - ac || a.localeCompare(b, 'ar')));
}
function hijriYear(issueDate) {
  const match = String(issueDate || '').match(/^(\d{4})\//u);
  return match ? `${match[1]} هـ` : '';
}
function toOfficialItem(row) {
  return {
    id: `boe_${row.boe_id}`,
    title: row.title,
    author: officialSource,
    investigator: '',
    publisher: officialSource,
    year: hijriYear(row.issue_date),
    link_telegram: '',
    link_drive: '',
    link_direct: row.official_url,
    source: officialSource,
    category: 'الأنظمة والتشريعات',
    material_type: 'نظام',
    file_type: 'رابط',
    file_size: '',
    pages_count: '',
    is_featured: false,
    download_links_count: 1,
    boe_id: row.boe_id,
    issue_date_hijri: row.issue_date || '',
    publication_date_hijri: row.publication_date || '',
    summary: row.summary || '',
  };
}

const [mainItemsText, publicItemsText, mainStatsText, publicStatsText, cacheText, addCsvText, deleteCsvText, manifestText] = await Promise.all([
  fs.readFile(paths.mainItems, 'utf8'), fs.readFile(paths.publicItems, 'utf8'),
  fs.readFile(paths.mainStats, 'utf8'), fs.readFile(paths.publicStats, 'utf8'),
  fs.readFile(paths.cache, 'utf8'), fs.readFile(paths.additions, 'utf8'),
  fs.readFile(paths.deletions, 'utf8'), fs.readFile(paths.manifest, 'utf8'),
]);
if (mainItemsText !== publicItemsText) throw new Error('النسخة الرئيسية والمنشورة للمواد غير متطابقتين قبل التنفيذ');
if (mainStatsText !== publicStatsText) throw new Error('النسخة الرئيسية والمنشورة للإحصاءات غير متطابقتين قبل التنفيذ');
const mainContainer = JSON.parse(mainItemsText);
const publicContainer = JSON.parse(publicItemsText);
const items = extractItems(mainContainer);
extractItems(publicContainer);
const mainStats = JSON.parse(mainStatsText);
const additions = parseCsv(addCsvText);
const deletions = parseCsv(deleteCsvText);
const manifest = JSON.parse(manifestText);
const currentById = new Map(items.map((item) => [item.id, item]));
const additionIds = new Set(additions.map((row) => row.boe_id));
const removalIds = new Set(deletions.map((row) => row.current_id));
const manifestAdditionIds = new Set(manifest.additions.map((row) => row.boe_id));
const manifestRemovalIds = new Set(manifest.deletions.map((row) => row.current_id));
const protectedMojIds = new Set(manifest.protected_moj.map((row) => row.id));

if (items.length !== expected.before) throw new Error(`إجمالي سابق غير متوقع: ${items.length}`);
if (additions.length !== expected.additions || additionIds.size !== expected.additions) throw new Error('قائمة الإضافة يجب أن تحوي 538 boe_id فريدة');
if (deletions.length !== expected.deletions || removalIds.size !== expected.deletions) throw new Error('قائمة الحذف يجب أن تحوي 226 current_id فريدة');
if (manifest.additions.length !== expected.additions || manifest.deletions.length !== expected.deletions) throw new Error('أعداد manifest لا تطابق المعتمد');
if (additionIds.size !== manifestAdditionIds.size || [...additionIds].some((id) => !manifestAdditionIds.has(id))) throw new Error('إضافات CSV لا تطابق manifest');
if (removalIds.size !== manifestRemovalIds.size || [...removalIds].some((id) => !manifestRemovalIds.has(id))) throw new Error('حذوف CSV لا تطابق manifest');
if (![...removalIds].every((id) => currentById.has(id))) throw new Error('يوجد current_id مفقود؛ يُمنع حذف بديل');
if ([...removalIds].some((id) => protectedMojIds.has(id))) throw new Error('قائمة الحذف تتضمن مادة محمية من وزارة العدل');
if (![...protectedMojIds].every((id) => currentById.has(id))) throw new Error('إحدى إضافات وزارة العدل الست غير موجودة قبل التنفيذ');
if (items.some((item) => String(item.id).startsWith('boe_'))) throw new Error('توجد إضافة هيئة خبراء سابقة؛ يُمنع تكرار الدفعة');
if (!additions.every((row) => row.decision === 'ADD_OFFICIAL_CANONICAL' && row.source === officialSource && row.official_url.startsWith(officialPrefix))) throw new Error('بيانات الإضافة الرسمية غير صالحة');
if (!deletions.every((row) => row.decision === 'DELETE_INTERMEDIARY_AFTER_ADDING_OFFICIAL')) throw new Error('قرار حذف وسيط غير صالح');
if (!cacheText.includes(oldCacheToken)) throw new Error('لم تُعثر معلمة كسر الكاش السابقة');

const officialItems = additions.map(toOfficialItem);
const newIds = new Set(officialItems.map((item) => item.id));
if (newIds.size !== expected.additions || [...newIds].some((id) => currentById.has(id))) throw new Error('تكرار معرف رسمي قبل الإضافة');
const finalItems = [...items, ...officialItems].filter((item) => !removalIds.has(item.id));
if (finalItems.length !== expected.after) throw new Error(`العدد النهائي غير متوقع: ${finalItems.length}`);
if (finalItems.some((item) => removalIds.has(item.id))) throw new Error('بقي سجل وسيط محدد بعد الحذف');
if (finalItems.filter((item) => String(item.id).startsWith('boe_')).length !== expected.additions) throw new Error('عدد السجلات الرسمية المضافة غير مطابق');
if (!protectedMojIds.size || ![...protectedMojIds].every((id) => finalItems.some((item) => item.id === id))) throw new Error('تضررت إضافات وزارة العدل المحمية');

const updatedStats = {
  ...mainStats,
  total_items: finalItems.length,
  categories: countBy(finalItems, 'category'),
  sources: countBy(finalItems, 'source'),
  material_types: countBy(finalItems, 'material_type'),
  file_types: countBy(finalItems, 'file_type'),
  featured_count: finalItems.filter((item) => item.is_featured).length,
  with_download_links: finalItems.filter((item) => Number(item.download_links_count || 0) > 0).length,
};
const updatedCache = cacheText.replaceAll(oldCacheToken, newCacheToken);

await Promise.all([
  fs.writeFile(paths.mainItems, JSON.stringify(rewrap(mainContainer, finalItems), null, 2) + '\n'),
  fs.writeFile(paths.publicItems, JSON.stringify(rewrap(publicContainer, finalItems), null, 2) + '\n'),
  fs.writeFile(paths.mainStats, JSON.stringify(updatedStats, null, 2) + '\n'),
  fs.writeFile(paths.publicStats, JSON.stringify(updatedStats, null, 2) + '\n'),
  fs.writeFile(paths.cache, updatedCache),
]);

const execution = {
  executed_at: new Date().toISOString(),
  source: officialSource,
  before_total: items.length,
  official_added: officialItems.length,
  intermediaries_removed: deletions.length,
  after_total: finalItems.length,
  cache_buster: newCacheToken,
  backup_directory: 'backups/boe_official_replacement_2026-09-29',
  additions: officialItems.map((item) => ({ id: item.id, boe_id: item.boe_id, title: item.title, official_url: item.link_direct })),
  deletions: deletions.map((row) => ({ id: row.current_id, title: row.current_title, official_boe_id: row.official_boe_id })),
  protected_moj_ids: [...protectedMojIds].sort(),
  before_sha256: sha256(mainItemsText),
};
await fs.writeFile(paths.execution, JSON.stringify(execution, null, 2) + '\n');
console.log(JSON.stringify({ before_total: execution.before_total, official_added: execution.official_added, intermediaries_removed: execution.intermediaries_removed, after_total: execution.after_total, cache_buster: execution.cache_buster }, null, 2));
