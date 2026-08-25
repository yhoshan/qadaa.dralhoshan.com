import { copyFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const requestedPath = '/home/ubuntu/upload/pasted_content_3.txt';
const requestedText = readFileSync(requestedPath, 'utf8');
const requestedIds = [...new Set(requestedText.match(/alexandria_cbz_\d+/g) ?? [])];
const expectedRequestedCount = 184;
if (requestedIds.length !== expectedRequestedCount) {
  throw new Error(`توقف آمن: استخرجت ${requestedIds.length} معرفاً بدلاً من ${expectedRequestedCount}.`);
}

const load = (file) => JSON.parse(readFileSync(path.join(root, file), 'utf8'));
const unwrap = (data) => Array.isArray(data) ? { items: data, wrapper: null } : { items: data.items ?? [], wrapper: data };
const normalize = (value) => String(value ?? '').replace(/[أإآ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه').replace(/\s+/g, ' ').trim().toLowerCase();
const isAlexandria = (item) => normalize(item.source) === 'مكتبه الاسكندريه';

const mainData = unwrap(load('items.json'));
const publicData = unwrap(load('client/public/items.json'));
const indexMain = new Map(mainData.items.map((item) => [item.id, item]));
const indexPublic = new Map(publicData.items.map((item) => [item.id, item]));
const found = requestedIds.filter((id) => indexMain.has(id)).map((id) => indexMain.get(id));
const missing = requestedIds.filter((id) => !indexMain.has(id));
const wrongSource = found.filter((item) => !isAlexandria(item)).map((item) => ({ id: item.id, source: item.source, title: item.title }));
const publicMissing = requestedIds.filter((id) => !indexPublic.has(id));
const publicWrongSource = requestedIds.filter((id) => indexPublic.has(id) && !isAlexandria(indexPublic.get(id))).map((id) => ({ id, source: indexPublic.get(id).source, title: indexPublic.get(id).title }));
const mainDuplicateIds = [...new Set(mainData.items.map((item) => item.id).filter((id, index, ids) => ids.indexOf(id) !== index))];
const safeToApply = wrongSource.length === 0 && publicWrongSource.length === 0 && mainDuplicateIds.length === 0;

const backupDir = path.join(root, 'backups', 'alexandria_184_targeted_removal_2026-08-24');
if (!existsSync(backupDir)) mkdirSync(backupDir, { recursive: true });
copyFileSync(path.join(root, 'items.json'), path.join(backupDir, 'items.before.json'));
copyFileSync(path.join(root, 'client/public/items.json'), path.join(backupDir, 'client-public-items.before.json'));
copyFileSync(path.join(root, 'stats.json'), path.join(backupDir, 'stats.before.json'));
copyFileSync(path.join(root, 'client/public/stats.json'), path.join(backupDir, 'client-public-stats.before.json'));

const precheck = {
  generated_at: new Date().toISOString(),
  requested_count: requestedIds.length,
  before_count: mainData.items.length,
  found_count: found.length,
  missing_count: missing.length,
  missing,
  wrong_source_count: wrongSource.length,
  wrong_source: wrongSource,
  public_missing_count: publicMissing.length,
  public_missing: publicMissing,
  public_wrong_source_count: publicWrongSource.length,
  public_wrong_source: publicWrongSource,
  duplicate_ids_before_removal: mainDuplicateIds,
  safe_to_apply: safeToApply,
  backup_dir: backupDir,
  found: found.map((item) => ({ id: item.id, title: item.title, source: item.source, category: item.category })),
};
writeFileSync(path.join(root, 'alexandria_184_removal_precheck.json'), `${JSON.stringify(precheck, null, 2)}\n`);
console.log(JSON.stringify({ requested_count: precheck.requested_count, found_count: precheck.found_count, missing_count: precheck.missing_count, wrong_source_count: precheck.wrong_source_count, safe_to_apply: precheck.safe_to_apply, backup_dir: precheck.backup_dir }, null, 2));
if (!safeToApply) throw new Error('توقف آمن: ظهر مصدر غير مطابق أو خلل بنيوي؛ لن ينفذ الحذف.');
