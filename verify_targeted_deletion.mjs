import { copyFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const mainPath = path.join(root, 'items.json');
const publicPath = path.join(root, 'client/public/items.json');
const backupDir = path.join(root, 'backups');
const reportPath = path.join(root, 'targeted_deletion_precheck.json');

const targets = [
  ['archive_4_20230212_20230212_2202', ['إقامة الدولة الإسلامية في ظل قانون السببية والسنن الإلهية والسنن التاريخية']],
  ['alexandria_cbz_22895', ['حزب اشتراكي ثوري للعمال والفلاحين لا يرقص للقرد في دولته']],
  ['alexandria_cbz_24852', ['تعزيز نظام لجنة الحزب']],
  ['alexandria_cbz_29818', ['فلسفة الثورة ودستور الغد']],
  ['alexandria_cbz_35915', ['اليمن بين القات وفساد الحكم قبل الثورة']],
  ['alexandria_cbz_66124', ['الصراع من أجل نظام سياسي جديد: مصر ما بعد الثورة']],
  ['arabialawer_18722', ['ثورة اليمن الدستورية']],
  ['alexandria_cbz_72662', ['من الدين إلى الطائفة في ضرورة الدولة المدنية']],
  ['alexandria_cbz_27440', ['النظام السياسي والإخوان المسلمون في مصر']],
  ['alexandria_cbz_22448', ['الإرهابيون قادمون', 'العنف']],
  ['alexandria_cbz_10902', ['النظام السياسي والمعارضة الإسلامية في مصر']],
  ['alexandria_cbz_18123', ['الناصرية والنظام العالمي الجديد']],
  ['alexandria_cbz_10881', ['نظام الحزب الواحد في أفريقيا بين النظرية والتطبيق']],
  ['alexandria_cbz_11004', ['حزب الأحرار الدستوريين 1922', '1953']],
  ['alexandria_cbz_15252', ['لائحة النظام الأساسي للحزب الوطني الديمقراطي']],
  ['alexandria_cbz_22258', ['الأحزاب الصغيرة والنظام الحزبي في مصر']],
  ['qadaa_3218', ['المحكمة الشرعية الفيدرالية بجمهورية باكستان تقرر القاديانية فئة كافرة']],
  ['alexandria_cbz_32176', ['ولاية الفقيه عند الشيعة الاثنى عشرية وموقف الإسلام منها']],
  ['alexandria_cbz_8450', ['خلف الحجاب: موقف الجماعات الإسلامية من قضية المرأة']],
  ['alexandria_cbz_27047', ['الدولة الإسلامية بين النظام الوطني الديمقراطي']],
];

const normalize = (value = '') => String(value)
  .normalize('NFKC')
  .replace(/[أإآٱ]/g, 'ا')
  .replace(/[ى]/g, 'ي')
  .replace(/[ً-ٟ]/g, '')
  .replace(/[ـ]/g, '')
  .replace(/[\p{P}\p{S}]/gu, ' ')
  .replace(/\s+/g, ' ')
  .trim()
  .toLowerCase();

const asArray = (data) => Array.isArray(data) ? data : (data.items ?? []);
const readItems = (file) => asArray(JSON.parse(readFileSync(file, 'utf8')));

if (!existsSync(mainPath) || !existsSync(publicPath)) {
  throw new Error('ملف البيانات الرئيسي أو النسخة المنشورة غير موجود.');
}

const mainItems = readItems(mainPath);
const publicItems = readItems(publicPath);
const mainById = new Map(mainItems.map((item) => [item.id, item]));
const publicById = new Map(publicItems.map((item) => [item.id, item]));

const duplicateIds = [...new Set(mainItems.map((item) => item.id).filter((id, index, all) => all.indexOf(id) !== index))];
const records = targets.map(([id, fragments]) => {
  const main = mainById.get(id);
  const published = publicById.get(id);
  const normalizedTitle = normalize(main?.title);
  const titleMatches = Boolean(main) && fragments.every((fragment) => normalizedTitle.includes(normalize(fragment)));
  return {
    id,
    expected_title_fragments: fragments,
    actual_title: main?.title ?? null,
    exists_main: Boolean(main),
    exists_published: Boolean(published),
    title_matches: titleMatches,
    published_title_matches_main: Boolean(main && published && normalize(main.title) === normalize(published.title)),
  };
});

const allVerified = records.every((record) => record.exists_main && record.exists_published && record.title_matches && record.published_title_matches_main)
  && duplicateIds.length === 0
  && mainItems.length === publicItems.length;

const report = {
  generated_at: new Date().toISOString(),
  main_count: mainItems.length,
  published_count: publicItems.length,
  target_count: targets.length,
  duplicate_ids_in_main: duplicateIds,
  all_verified: allVerified,
  records,
};

if (allVerified) {
  mkdirSync(backupDir, { recursive: true });
  copyFileSync(mainPath, path.join(backupDir, 'items.before-targeted-deletion.json'));
  copyFileSync(publicPath, path.join(backupDir, 'client-public-items.before-targeted-deletion.json'));
  report.backups = [
    'backups/items.before-targeted-deletion.json',
    'backups/client-public-items.before-targeted-deletion.json',
  ];
}

writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify({ all_verified: allVerified, main_count: mainItems.length, target_count: targets.length, report: path.basename(reportPath) }, null, 2));

if (!allVerified) process.exitCode = 2;
