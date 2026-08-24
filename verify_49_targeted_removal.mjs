import { copyFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const mainPath = path.join(root, 'items.json');
const publicPath = path.join(root, 'client/public/items.json');
const backupDir = path.join(root, 'backups');

const targetIds = [
  'legal_mag_196', 'legal_mag_201', 'legal_mag_202', 'legal_mag_203', 'legal_mag_204',
  'legal_mag_207', 'legal_mag_208', 'legal_mag_212', 'legal_mag_213', 'legal_mag_217',
  'legal_mag_227', 'legal_mag_233', 'legal_mag_237', 'legal_mag_238', 'legal_mag_239',
  'legal_mag_240', 'legal_mag_241', 'legal_mag_242', 'legal_mag_244', 'legal_mag_245',
  'legal_mag_246', 'legal_mag_252', 'legal_mag_259', 'legal_mag_260', 'legal_mag_261',
  'legal_mag_263', 'legal_mag_264', 'legal_mag_265', 'legal_mag_266', 'legal_mag_267',
  'legal_mag_268', 'legal_mag_269', 'legal_mag_270', 'legal_mag_272', 'legal_mag_273',
  'alexandria_cbz_9566', 'alexandria_cbz_30657', 'alexandria_cbz_64598', 'alexandria_cbz_24605',
  'alexandria_cbz_63753', 'alexandria_cbz_20559', 'alexandria_cbz_28851', 'alexandria_cbz_22918',
  'alexandria_cbz_9769', 'alexandria_cbz_22793', 'alexandria_cbz_61793', 'alexandria_cbz_26393',
  'alexandria_cbz_30602', 'alexandria_cbz_62017',
];
const targetSet = new Set(targetIds);
const parseItems = (file) => {
  const data = JSON.parse(readFileSync(file, 'utf8'));
  return Array.isArray(data) ? data : data.items;
};
if (!existsSync(mainPath) || !existsSync(publicPath)) throw new Error('ملف البيانات الرئيسي أو النسخة المنشورة غير موجود.');
const main = parseItems(mainPath);
const published = parseItems(publicPath);
const mainById = new Map(main.map((item) => [item.id, item]));
const publicById = new Map(published.map((item) => [item.id, item]));
const found = targetIds.filter((id) => mainById.has(id)).map((id) => ({
  id,
  title: mainById.get(id).title,
  source: mainById.get(id).source,
  category: mainById.get(id).category,
  exists_published: publicById.has(id),
  published_matches: publicById.has(id) && JSON.stringify(mainById.get(id)) === JSON.stringify(publicById.get(id)),
}));
const missing = targetIds.filter((id) => !mainById.has(id));
const idsOutsideTarget = main.filter((item) => targetSet.has(item.id) === false && false).map((item) => item.id);
const safeToApply = found.every((item) => item.exists_published && item.published_matches);

mkdirSync(backupDir, { recursive: true });
copyFileSync(mainPath, path.join(backupDir, 'items.before-49-targeted-removal.json'));
copyFileSync(publicPath, path.join(backupDir, 'client-public-items.before-49-targeted-removal.json'));

const report = {
  generated_at: new Date().toISOString(),
  before_count: main.length,
  target_count: targetIds.length,
  found_count: found.length,
  missing_count: missing.length,
  safe_to_apply: safeToApply,
  found,
  missing,
  backups: [
    'backups/items.before-49-targeted-removal.json',
    'backups/client-public-items.before-49-targeted-removal.json',
  ],
  no_non_target_selection: idsOutsideTarget.length === 0,
};
writeFileSync('targeted_49_removal_precheck.json', `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify({ before_count: main.length, target_count: targetIds.length, found_count: found.length, missing_count: missing.length, safe_to_apply: safeToApply }, null, 2));
if (!safeToApply) process.exitCode = 2;
