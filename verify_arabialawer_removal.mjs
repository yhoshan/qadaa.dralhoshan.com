import { copyFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const mainPath = path.join(root, 'items.json');
const publicPath = path.join(root, 'client/public/items.json');
const reportPath = path.join(root, 'arabialawer_removal_precheck.json');
const backupDir = path.join(root, 'backups');

const normalize = (value = '') => String(value)
  .normalize('NFKC')
  .replace(/[أإآٱ]/g, 'ا')
  .replace(/ة/g, 'ه')
  .replace(/ى/g, 'ي')
  .replace(/[ً-ٟـ]/g, '')
  .replace(/[\p{P}\p{S}\s_]/gu, '')
  .toLowerCase();

const parseItems = (file) => {
  const data = JSON.parse(readFileSync(file, 'utf8'));
  return Array.isArray(data) ? data : data.items;
};

const matchesTarget = (item) => {
  const idMatch = String(item.id ?? '').toLowerCase().startsWith('arabialawer_');
  const entityText = [item.source, item.publisher, item.organization, item.entity, item.institution, item.agency]
    .filter(Boolean)
    .join(' ');
  const sourceMatch = normalize(entityText).includes('arabialawer') || normalize(entityText).includes('اكاديميهالمحاماه');
  return { idMatch, sourceMatch, matched: idMatch || sourceMatch };
};

if (!existsSync(mainPath) || !existsSync(publicPath)) throw new Error('ملف البيانات الرئيسي أو النسخة المنشورة غير موجود.');
const main = parseItems(mainPath);
const published = parseItems(publicPath);
const publicById = new Map(published.map((item) => [item.id, item]));
const duplicates = [...new Set(main.map((item) => item.id).filter((id, index, all) => all.indexOf(id) !== index))];
const targets = main.filter((item) => matchesTarget(item).matched).map((item) => ({
  id: item.id,
  title: item.title,
  source: item.source,
  category: item.category,
  matched_by: Object.entries(matchesTarget(item)).filter(([, value]) => value === true).map(([key]) => key),
  exists_published: publicById.has(item.id),
  published_matches: publicById.has(item.id) && JSON.stringify(publicById.get(item.id)) === JSON.stringify(item),
}));
const mainIds = new Set(main.map((item) => item.id));
const publicIds = new Set(published.map((item) => item.id));
const idSetMatches = mainIds.size === publicIds.size && [...mainIds].every((id) => publicIds.has(id));
const allVerified = targets.length > 0 && targets.every((target) => target.exists_published && target.published_matches) && duplicates.length === 0 && idSetMatches;

const report = {
  generated_at: new Date().toISOString(),
  before_count: main.length,
  published_count: published.length,
  matched_count: targets.length,
  matched_by_id_prefix: targets.filter((target) => target.matched_by.includes('idMatch')).length,
  matched_by_source_or_entity: targets.filter((target) => target.matched_by.includes('sourceMatch')).length,
  duplicate_ids: duplicates,
  main_and_published_ids_match: idSetMatches,
  all_verified: allVerified,
  targets,
};

if (allVerified) {
  mkdirSync(backupDir, { recursive: true });
  copyFileSync(mainPath, path.join(backupDir, 'items.before-arabialawer-removal.json'));
  copyFileSync(publicPath, path.join(backupDir, 'client-public-items.before-arabialawer-removal.json'));
  report.backups = [
    'backups/items.before-arabialawer-removal.json',
    'backups/client-public-items.before-arabialawer-removal.json',
  ];
}

writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify({ all_verified: allVerified, before_count: main.length, matched_count: targets.length, report: path.basename(reportPath) }, null, 2));
if (!allVerified) process.exitCode = 2;
