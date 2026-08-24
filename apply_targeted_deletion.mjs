import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const precheckPath = path.join(root, 'targeted_deletion_precheck.json');
const mainPath = path.join(root, 'items.json');
const publicPath = path.join(root, 'client/public/items.json');
const statsPath = path.join(root, 'stats.json');
const publicStatsPath = path.join(root, 'client/public/stats.json');
const reportPath = path.join(root, 'targeted_deletion_execution_report.json');

if (!existsSync(precheckPath)) throw new Error('لا يوجد تقرير تحقق مسبق. شغّل verify_targeted_deletion.mjs أولاً.');
const precheck = JSON.parse(readFileSync(precheckPath, 'utf8'));
if (!precheck.all_verified || precheck.target_count !== 20) throw new Error('فشل التحقق المسبق؛ لن يتم حذف أي سجل.');

const targetIds = new Set(precheck.records.map((record) => record.id));
const parse = (file) => JSON.parse(readFileSync(file, 'utf8'));
const unwrap = (data) => Array.isArray(data) ? { items: data, wrap: null } : { items: data.items ?? [], wrap: data };
const rewrap = ({ items, wrap }) => wrap ? { ...wrap, items } : items;

const mainData = unwrap(parse(mainPath));
const publicData = unwrap(parse(publicPath));
const removedMain = mainData.items.filter((item) => targetIds.has(item.id));
const removedPublic = publicData.items.filter((item) => targetIds.has(item.id));

if (removedMain.length !== 20 || removedPublic.length !== 20) {
  throw new Error(`رفض الحذف: وجدنا ${removedMain.length} في الرئيسي و${removedPublic.length} في المنشور بدلاً من 20.`);
}

const nextMain = mainData.items.filter((item) => !targetIds.has(item.id));
const nextPublic = publicData.items.filter((item) => !targetIds.has(item.id));
if (nextMain.length !== precheck.main_count - 20 || nextPublic.length !== precheck.published_count - 20) {
  throw new Error('العداد بعد الحذف لا يطابق العدد المتوقع؛ لن تتم الكتابة.');
}

const updateStats = (file) => {
  if (!existsSync(file)) return null;
  const stats = parse(file);
  return { ...stats, total_items: nextMain.length };
};

writeFileSync(mainPath, `${JSON.stringify(rewrap({ ...mainData, items: nextMain }), null, 2)}\n`);
writeFileSync(publicPath, `${JSON.stringify(rewrap({ ...publicData, items: nextPublic }), null, 2)}\n`);

const nextStats = updateStats(statsPath);
const nextPublicStats = updateStats(publicStatsPath);
if (nextStats) writeFileSync(statsPath, `${JSON.stringify(nextStats, null, 2)}\n`);
if (nextPublicStats) writeFileSync(publicStatsPath, `${JSON.stringify(nextPublicStats, null, 2)}\n`);

const finalIds = new Set(nextMain.map((item) => item.id));
const duplicateIds = [...new Set(nextMain.map((item) => item.id).filter((id, index, all) => all.indexOf(id) !== index))];
const report = {
  generated_at: new Date().toISOString(),
  before_count: precheck.main_count,
  verified_target_count: precheck.records.length,
  deleted_count: removedMain.length,
  final_count: nextMain.length,
  removed: removedMain.map((item) => ({ id: item.id, title: item.title })),
  absent_after_deletion: [...targetIds].every((id) => !finalIds.has(id)),
  duplicate_ids_after_deletion: duplicateIds,
  non_target_records_preserved_by_count: nextMain.length === precheck.main_count - targetIds.size,
};
writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify(report, null, 2));
