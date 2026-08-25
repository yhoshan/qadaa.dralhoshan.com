import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const load = (file) => JSON.parse(readFileSync(path.join(root, file), 'utf8'));
const save = (file, data) => writeFileSync(path.join(root, file), `${JSON.stringify(data, null, 2)}\n`);
const unwrap = (raw) => Array.isArray(raw) ? raw : raw.items;
const rewrap = (raw, items) => Array.isArray(raw) ? items : { ...raw, items };
const mainRaw = load('items.json');
const publicRaw = load('client/public/items.json');
const statsBefore = load('stats.json');
const manifest = load('iirmll_9_duplicate_removal_manifest.json');
const main = unwrap(mainRaw);
const published = unwrap(publicRaw);
const removalSet = new Set(manifest.removal_ids);
const protectedSet = new Set(manifest.protected_ids);
const assert = (condition, message) => { if (!condition) throw new Error(message); };
assert(main.length === manifest.expected.total_before && published.length === manifest.expected.total_before, 'العدد القبلي لا يطابق الحالة المعتمدة 11,295.');
assert(new Set(main.map((item) => item.id)).size === main.length, 'توجد معرفات مكررة في النسخة الرئيسية قبل الحذف.');
assert(new Set(published.map((item) => item.id)).size === published.length, 'توجد معرفات مكررة في النسخة المنشورة قبل الحذف.');
const mainById = new Map(main.map((item) => [item.id, item]));
const publishedById = new Map(published.map((item) => [item.id, item]));
for (const id of manifest.removal_ids) {
  const item = mainById.get(id);
  assert(item, `المعرف المطلوب غير موجود في النسخة الرئيسية: ${id}`);
  assert(publishedById.has(id), `المعرف المطلوب غير موجود في النسخة المنشورة: ${id}`);
  assert(item.source === manifest.source && String(item.link_telegram ?? '').includes(manifest.required_telegram_fragment), `المعرف خارج نطاق مصدر iirmll: ${id}`);
}
for (const id of manifest.protected_ids) assert(mainById.has(id) && publishedById.has(id), `معرف محمي مفقود: ${id}`);
const removed = manifest.removal_ids.map((id) => mainById.get(id));
const nextMain = main.filter((item) => !removalSet.has(item.id));
const nextPublished = published.filter((item) => !removalSet.has(item.id));
assert(nextMain.length === manifest.expected.total_after && nextPublished.length === manifest.expected.total_after, 'العدد البعدي لا يطابق 11,286.');
assert(nextMain.every((item) => !removalSet.has(item.id)) && nextPublished.every((item) => !removalSet.has(item.id)), 'بقي معرف مطلوب حذفه بعد التصفية.');
assert([...protectedSet].every((id) => nextMain.some((item) => item.id === id) && nextPublished.some((item) => item.id === id)), 'حُذف سجل محمي أو فقد من النسخة المنشورة.');
const category = (item) => String(item.category ?? 'عام');
const countBy = (items, key, fallback) => Object.fromEntries([...items.reduce((map, item) => { const name = String(item[key] ?? fallback).trim() || fallback; map.set(name, (map.get(name) ?? 0) + 1); return map; }, new Map()).entries()].sort((a, b) => a[0].localeCompare(b[0], 'ar')));
const stats = {
  total_items: nextMain.length,
  qadaa_count: nextMain.filter((item) => /قضاء|قضائي/.test(category(item))).length,
  nizam_count: nextMain.filter((item) => /نظام|لائحة|تشريع/.test(category(item))).length,
  mohama_count: nextMain.filter((item) => /محاماة|محامي/.test(category(item))).length,
  other_count: 0,
  books_count: nextMain.length,
  audio_count: 0,
  video_count: 0,
  categories: countBy(nextMain, 'category', 'عام'),
  sources: countBy(nextMain, 'source', 'غير محدد'),
  file_types: countBy(nextMain, 'file_type', 'غير محدد'),
  featured_count: nextMain.filter((item) => item.is_featured).length,
  with_download_links: nextMain.filter((item) => item.link_telegram || item.link_drive || item.link_direct).length,
};
stats.other_count = Math.max(0, stats.total_items - stats.qadaa_count - stats.nizam_count - stats.mohama_count);
assert(stats.sources[manifest.source] === manifest.expected.source_after, `عدد مصدر iirmll بعد الحذف غير صحيح: ${stats.sources[manifest.source]}`);
save('items.json', rewrap(mainRaw, nextMain));
save('client/public/items.json', rewrap(publicRaw, nextPublished));
save('stats.json', stats);
save('client/public/stats.json', stats);
const output = {
  generated_at: new Date().toISOString(),
  total_before: main.length,
  total_after: nextMain.length,
  iirmll_before: main.filter((item) => item.source === manifest.source && String(item.link_telegram ?? '').includes(manifest.required_telegram_fragment)).length,
  iirmll_after: stats.sources[manifest.source],
  removed_count: removed.length,
  removed: removed.map((item) => ({ id: item.id, title: item.title, source: item.source, category: item.category, link_telegram: item.link_telegram })),
  protected_ids_verified: manifest.protected_ids,
  stats_before_total: statsBefore.total_items,
};
save('iirmll_9_duplicate_removal_execution.json', output);
console.log(JSON.stringify(output, null, 2));
