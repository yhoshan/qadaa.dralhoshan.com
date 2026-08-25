import { readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const load = (file) => JSON.parse(readFileSync(path.join(root, file), 'utf8'));
const unwrap = (data) => Array.isArray(data) ? { items: data, wrapper: null } : { items: data.items ?? [], wrapper: data };
const rewrap = ({ items, wrapper }) => wrapper ? { ...wrapper, items } : items;
const countBy = (items, selector) => Object.fromEntries([...items.reduce((map, item) => {
  const key = selector(item) || 'غير مصنف'; map.set(key, (map.get(key) ?? 0) + 1); return map;
}, new Map())].sort((a, b) => String(a[0]).localeCompare(String(b[0]), 'ar')));
const category = (item) => String(item.category ?? '');
const manifest = load('restart_recovery_removal_manifest.json');
const precheck = load('restart_recovery_precheck.json');
if (!precheck.passed) throw new Error('فشل التحقق القبلي؛ لن تنفذ الاستعادة.');
const targetIds = new Set(manifest.all_target_ids);
const protectedIds = new Set(manifest.protected_ids);
const isExpected = (item) => String(item.id).startsWith('great_law_') ? item.source === 'المكتبة القانونية الكبرى' : String(item.id).startsWith('risail_') ? item.source === 'قناة الرسائل العلمية' && String(item.link_telegram ?? '').includes('t.me/c/1453973283') : false;
const main = unwrap(load('items.json'));
const publicData = unwrap(load('client/public/items.json'));
const beforeMainIds = new Set(main.items.map((item) => item.id));
const beforePublicIds = new Set(publicData.items.map((item) => item.id));
const foundMain = main.items.filter((item) => targetIds.has(item.id));
const foundPublic = publicData.items.filter((item) => targetIds.has(item.id));
if (main.items.length !== precheck.before_count || publicData.items.length !== precheck.before_count || foundMain.length !== targetIds.size || foundPublic.length !== targetIds.size || foundMain.some((item) => !isExpected(item)) || foundPublic.some((item) => !isExpected(item))) throw new Error('حالة البيانات تغيرت بعد التحقق؛ توقف آمن.');
if ([...protectedIds].some((id) => !beforeMainIds.has(id) || !beforePublicIds.has(id))) throw new Error('معرف محمي مفقود قبل الاستعادة؛ توقف آمن.');
const nextMain = main.items.filter((item) => !targetIds.has(item.id));
const nextPublic = publicData.items.filter((item) => !targetIds.has(item.id));
if (nextMain.length !== manifest.expected_after_count || nextPublic.length !== manifest.expected_after_count) throw new Error('فشل تحقق العدد النهائي؛ لن تتم الكتابة.');
const afterMainIds = new Set(nextMain.map((item) => item.id));
const afterPublicIds = new Set(nextPublic.map((item) => item.id));
if ([...targetIds].some((id) => afterMainIds.has(id) || afterPublicIds.has(id)) || [...protectedIds].some((id) => !afterMainIds.has(id) || !afterPublicIds.has(id))) throw new Error('توقف آمن: لم تتحقق حماية المعرفات أو إزالة الأهداف.');
const unexpectedMainLosses = [...beforeMainIds].filter((id) => !afterMainIds.has(id) && !targetIds.has(id));
const unexpectedPublicLosses = [...beforePublicIds].filter((id) => !afterPublicIds.has(id) && !targetIds.has(id));
if (unexpectedMainLosses.length || unexpectedPublicLosses.length) throw new Error('توقف آمن: فقد خارج القائمة المحددة.');
const stats = {
  total_items: nextMain.length,
  qadaa_count: nextMain.filter((item) => /قضاء|قضائي/.test(category(item))).length,
  nizam_count: nextMain.filter((item) => /نظام|لائحة|تشريع/.test(category(item))).length,
  mohama_count: nextMain.filter((item) => /محاماة|محامي/.test(category(item))).length,
  other_count: 0,
  books_count: nextMain.length, audio_count: 0, video_count: 0,
  categories: countBy(nextMain, (item) => item.category), sources: countBy(nextMain, (item) => item.source), file_types: countBy(nextMain, (item) => item.file_type),
  featured_count: nextMain.filter((item) => item.is_featured).length,
  with_download_links: nextMain.filter((item) => item.link_telegram || item.link_drive || item.link_direct).length,
};
stats.other_count = Math.max(0, stats.total_items - stats.qadaa_count - stats.nizam_count - stats.mohama_count);
writeFileSync(path.join(root, 'items.json'), `${JSON.stringify(rewrap({ ...main, items: nextMain }), null, 2)}\n`);
writeFileSync(path.join(root, 'client/public/items.json'), `${JSON.stringify(rewrap({ ...publicData, items: nextPublic }), null, 2)}\n`);
writeFileSync(path.join(root, 'stats.json'), `${JSON.stringify(stats, null, 2)}\n`);
writeFileSync(path.join(root, 'client/public/stats.json'), `${JSON.stringify(stats, null, 2)}\n`);
const cacheVersion = 'recovery-great-law-31-academic-theses-30-2026-08-25';
const hookPath = path.join(root, 'client/src/hooks/useItems.ts');
const hook = readFileSync(hookPath, 'utf8');
writeFileSync(hookPath, hook.replace(/v=[^'"`)+]+/g, `v=${cacheVersion}`));
const removed = foundMain.map((item) => ({ id: item.id, title: item.title, source: item.source, removal_type: manifest.targets.great_law.subject.includes(item.id) || manifest.targets.academic_theses.subject.includes(item.id) ? 'موضوعي' : 'تكرار زائد' }));
const report = {
  generated_at: new Date().toISOString(), before_count: main.items.length, removed_count: removed.length, final_count: nextMain.length,
  great_law_removed: removed.filter((item) => item.id.startsWith('great_law_')).length,
  academic_theses_removed: removed.filter((item) => item.id.startsWith('risail_')).length,
  removed, protected_remaining: [...protectedIds].map((id) => ({ id, title: nextMain.find((item) => item.id === id)?.title ?? null })),
  remaining_target_ids: [...targetIds].filter((id) => afterMainIds.has(id)), unexpected_main_losses: unexpectedMainLosses, unexpected_public_losses: unexpectedPublicLosses,
  source_counts_after: { great_law: nextMain.filter((item) => item.source === 'المكتبة القانونية الكبرى').length, academic_theses: nextMain.filter((item) => item.source === 'قناة الرسائل العلمية').length },
  cache_version: cacheVersion,
};
writeFileSync(path.join(root, 'restart_recovery_execution_report.json'), `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify({ before: report.before_count, removed: report.removed_count, final: report.final_count, great_law_removed: report.great_law_removed, academic_theses_removed: report.academic_theses_removed, source_counts_after: report.source_counts_after }, null, 2));
