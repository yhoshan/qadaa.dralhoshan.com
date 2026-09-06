import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';

const root = process.cwd();
const manifestPath = '/home/ubuntu/upload/pasted_file_RkJXqY_qadaa_delete_manifest.json';
const parse = async (file) => JSON.parse(await fs.readFile(file, 'utf8'));
const unwrap = (data) => Array.isArray(data) ? data : data.items;
const hash = (value) => crypto.createHash('sha256').update(JSON.stringify(value)).digest('hex');

const [manifest, mainData, publicData] = await Promise.all([
  parse(manifestPath),
  parse(path.join(root, 'items.json')),
  parse(path.join(root, 'client/public/items.json')),
]);
const targets = manifest.items;
const targetIds = targets.map((item) => String(item.id));
const duplicateTargetIds = targetIds.filter((id, index) => targetIds.indexOf(id) !== index);
const invalidDecisions = targets.filter((item) => item.decision !== 'DELETE').map((item) => item.id);
const mainItems = unwrap(mainData);
const publicItems = unwrap(publicData);
if (!Array.isArray(mainItems) || !Array.isArray(publicItems)) throw new Error('بنية ملف البيانات غير متوقعة.');
const mainById = new Map(mainItems.map((item) => [String(item.id), item]));
const publicById = new Map(publicItems.map((item) => [String(item.id), item]));
const found = targets.filter((target) => mainById.has(String(target.id)) && publicById.has(String(target.id)));
const missingMain = targets.filter((target) => !mainById.has(String(target.id))).map((item) => item.id);
const missingPublic = targets.filter((target) => !publicById.has(String(target.id))).map((item) => item.id);
const mismatchedLocations = targets.filter((target) => mainById.has(String(target.id)) !== publicById.has(String(target.id))).map((item) => item.id);
const mismatchedTitles = found.filter((target) => String(mainById.get(String(target.id)).title ?? '') !== String(target.title ?? '')).map((target) => ({
  id: target.id,
  manifest_title: target.title,
  current_title: mainById.get(String(target.id)).title,
}));
const duplicateExistingIds = [...new Set(mainItems.map((item) => String(item.id)).filter((id, index, all) => all.indexOf(id) !== index))];
const report = {
  generated_at: new Date().toISOString(),
  manifest_count_field: manifest.count,
  target_count: targets.length,
  expected_before_count: 17360,
  main_before_count: mainItems.length,
  public_before_count: publicItems.length,
  target_ids_unique: duplicateTargetIds.length === 0,
  invalid_decisions: invalidDecisions,
  targets_found_in_both: found.length,
  missing_in_main: missingMain,
  missing_in_public: missingPublic,
  ids_in_only_one_copy: mismatchedLocations,
  title_mismatches_for_recording_only: mismatchedTitles,
  main_public_data_match: hash(mainItems) === hash(publicItems),
  duplicate_existing_ids: duplicateExistingIds,
  exact_removal_scope: found.map((target) => {
    const item = mainById.get(String(target.id));
    return { id: item.id, title: item.title, source: item.source, category: item.category };
  }),
};
report.all_verified = report.manifest_count_field === 188
  && report.target_count === 188
  && report.main_before_count === 17360
  && report.public_before_count === 17360
  && report.target_ids_unique
  && report.invalid_decisions.length === 0
  && report.targets_found_in_both === 188
  && report.missing_in_main.length === 0
  && report.missing_in_public.length === 0
  && report.ids_in_only_one_copy.length === 0
  && report.main_public_data_match
  && report.duplicate_existing_ids.length === 0;

await fs.writeFile(path.join(root, 'qadaa_delete_manifest_precheck.json'), `${JSON.stringify(report, null, 2)}\n`);
const lines = [
  'الفحص المسبق لقائمة الحذف المحددة بالمعرّفات فقط',
  `تاريخ الفحص: ${report.generated_at}`,
  `عدد القائمة: ${report.target_count}`,
  `عدد المواد قبل الحذف: ${report.main_before_count}`,
  `المعرّفات الموجودة في النسختين: ${report.targets_found_in_both}`,
  `المعرّفات المفقودة في الرئيسية: ${report.missing_in_main.length}`,
  `المعرّفات المفقودة في المنشورة: ${report.missing_in_public.length}`,
  `العناوين المختلفة عن ملف الحذف (للتوثيق فقط ولا تؤثر في الحذف بالمعرّف): ${report.title_mismatches_for_recording_only.length}`,
  `نجاح الفحص: ${report.all_verified ? 'نعم' : 'لا'}`,
  '',
  'المعرّفات الجاهزة للحذف:',
  ...report.exact_removal_scope.map((item) => `${item.id} | ${item.title} | ${item.source} | ${item.category}`),
];
await fs.writeFile(path.join(root, 'qadaa_delete_manifest_precheck.txt'), lines.join('\n'));
console.log(JSON.stringify({ all_verified: report.all_verified, target_count: report.target_count, found: report.targets_found_in_both, main_before_count: report.main_before_count, title_mismatches: report.title_mismatches_for_recording_only.length }, null, 2));
if (!report.all_verified) process.exitCode = 1;
