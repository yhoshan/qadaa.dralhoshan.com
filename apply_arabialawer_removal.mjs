import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const precheck = JSON.parse(readFileSync(path.join(root, 'arabialawer_removal_precheck.json'), 'utf8'));
if (!precheck.all_verified || precheck.matched_count < 1) throw new Error('فشل التحقق المسبق؛ لن يتم حذف أي سجل.');

const targetIds = new Set(precheck.targets.map((target) => target.id));
const parse = (file) => JSON.parse(readFileSync(path.join(root, file), 'utf8'));
const unwrap = (data) => Array.isArray(data) ? { items: data, wrapper: null } : { items: data.items ?? [], wrapper: data };
const rewrap = ({ items, wrapper }) => wrapper ? { ...wrapper, items } : items;
const normalize = (value = '') => String(value)
  .normalize('NFKC').replace(/[أإآٱ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي')
  .replace(/[ً-ٟـ]/g, '').replace(/[\p{P}\p{S}\s_]/gu, '').toLowerCase();
const isTarget = (item) => {
  const idMatch = String(item.id ?? '').toLowerCase().startsWith('arabialawer_');
  const entityText = [item.source, item.publisher, item.organization, item.entity, item.institution, item.agency].filter(Boolean).join(' ');
  const sourceMatch = normalize(entityText).includes('arabialawer') || normalize(entityText).includes('اكاديميهالمحاماه');
  return idMatch || sourceMatch;
};

const mainData = unwrap(parse('items.json'));
const publicData = unwrap(parse('client/public/items.json'));
const removedMain = mainData.items.filter(isTarget);
const removedPublic = publicData.items.filter(isTarget);
if (removedMain.length !== precheck.matched_count || removedPublic.length !== precheck.matched_count) {
  throw new Error(`رفض الحذف: العدد الحالي المطابق لا يساوي الحصر المسبق (${removedMain.length}/${removedPublic.length} مقابل ${precheck.matched_count}).`);
}
if (!removedMain.every((item) => targetIds.has(item.id)) || !removedPublic.every((item) => targetIds.has(item.id))) {
  throw new Error('رفض الحذف: ظهرت سجلات جديدة مطابقة خارج قائمة التحقق المسبق.');
}

const nextMain = mainData.items.filter((item) => !isTarget(item));
const nextPublic = publicData.items.filter((item) => !isTarget(item));
const expectedCount = precheck.before_count - precheck.matched_count;
if (nextMain.length !== expectedCount || nextPublic.length !== expectedCount) throw new Error('فشل تحقق العدد النهائي؛ لن تتم الكتابة.');

const countBy = (items, selector) => Object.fromEntries([...items.reduce((map, item) => {
  const key = selector(item) || 'غير مصنف';
  map.set(key, (map.get(key) ?? 0) + 1);
  return map;
}, new Map())].sort((a, b) => String(a[0]).localeCompare(String(b[0]), 'ar')));
const category = (item) => String(item.category ?? '');
const stats = {
  total_items: nextMain.length,
  qadaa_count: nextMain.filter((item) => /قضاء|قضائي/.test(category(item))).length,
  nizam_count: nextMain.filter((item) => /نظام|لائحة|تشريع/.test(category(item))).length,
  mohama_count: nextMain.filter((item) => /محاماة|محامي/.test(category(item))).length,
  other_count: 0,
  books_count: nextMain.length,
  audio_count: 0,
  video_count: 0,
  categories: countBy(nextMain, (item) => item.category),
  sources: countBy(nextMain, (item) => item.source),
  file_types: countBy(nextMain, (item) => item.file_type),
  featured_count: nextMain.filter((item) => item.is_featured).length,
  with_download_links: nextMain.filter((item) => item.link_telegram || item.link_drive || item.link_direct).length,
};
stats.other_count = Math.max(0, stats.total_items - stats.qadaa_count - stats.nizam_count - stats.mohama_count);

writeFileSync('items.json', `${JSON.stringify(rewrap({ ...mainData, items: nextMain }), null, 2)}\n`);
writeFileSync('client/public/items.json', `${JSON.stringify(rewrap({ ...publicData, items: nextPublic }), null, 2)}\n`);
writeFileSync('stats.json', `${JSON.stringify(stats, null, 2)}\n`);
writeFileSync('client/public/stats.json', `${JSON.stringify(stats, null, 2)}\n`);

const hookPath = path.join(root, 'client/src/hooks/useItems.ts');
const hook = readFileSync(hookPath, 'utf8');
const cacheVersion = 'arabialawer-removal-2026-08-24';
writeFileSync(hookPath, hook.replace(/v=[^'"`)+]+/g, `v=${cacheVersion}`));

const duplicates = [...new Set(nextMain.map((item) => item.id).filter((id, index, all) => all.indexOf(id) !== index))];
const report = {
  generated_at: new Date().toISOString(),
  before_count: precheck.before_count,
  found_count: precheck.matched_count,
  removed_count: removedMain.length,
  final_count: nextMain.length,
  final_source_matches: nextMain.filter(isTarget).length,
  remaining_prefixed_ids: nextMain.filter((item) => String(item.id ?? '').toLowerCase().startsWith('arabialawer_')).map((item) => item.id),
  remaining_matching_sources: nextMain.filter((item) => normalize([item.source, item.publisher, item.organization, item.entity, item.institution, item.agency].filter(Boolean).join(' ')).includes('arabialawer') || normalize([item.source, item.publisher, item.organization, item.entity, item.institution, item.agency].filter(Boolean).join(' ')).includes('اكاديميهالمحاماه')).map((item) => ({ id: item.id, source: item.source })),
  duplicate_ids_after_deletion: duplicates,
  non_target_records_preserved_by_count: nextMain.length === expectedCount,
  removed_source_values: countBy(removedMain, (item) => item.source),
  cache_version: cacheVersion,
};
writeFileSync('arabialawer_removal_execution_report.json', `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify(report, null, 2));
