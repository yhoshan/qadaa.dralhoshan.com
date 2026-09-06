import { readFile, writeFile } from 'node:fs/promises';

const root = process.cwd();
const uploadRoot = '/home/ubuntu/upload';
const unwrap = (raw) => Array.isArray(raw) ? raw : raw.items;
const normalizeText = (value = '') => String(value).toLowerCase().normalize('NFKD').replace(/[\u064B-\u065F\u0670]/g, '').replace(/[أإآ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي').replace(/[\s\W_]+/g, '');
const normalizeUrl = (value = '') => String(value).trim().replace(/#.*$/, '').replace(/\/$/, '').toLowerCase();
const files = {
  five_batches: [
    'pasted_file_Ccz0Dd_moj_official_journals_new_titles_2026-08-28.json',
    'pasted_file_DsF63l_lawlibrarysa_MASTER_v6_merge_ready_310.json',
    'pasted_file_SvnUyP_lawlibrarysa_merge_ready_140.json',
    'pasted_file_iRj0dd_kku_uqu_legal_new_titles_2026-08-28.json',
    'pasted_file_VzsweO_ksu_law_political_science_new_titles_2026-08-28.json',
  ],
  kau_qassim: ['pasted_file_RMtfOF_kau_qassim_legal_new_titles_2026-08-28.json'],
  ajsrp: ['pasted_file_OsPkHo_ajsrp_saudi_legal_new_titles_24_2026-08-28.json'],
  majmaah_imam: ['pasted_file_7JojVM_majmaah_imam_legal_new_titles_2026-08-28.json'],
};
const existing = unwrap(JSON.parse(await readFile(`${root}/items.json`, 'utf8')));
const existingTitles = new Set(existing.map((item) => normalizeText(item.title)));
const existingUrls = new Set(existing.map((item) => normalizeUrl(item.link_direct || item.link_drive || item.link_telegram)).filter(Boolean));
const output = { created_at: new Date().toISOString(), current_total: existing.length, groups: {}, initial_site_recovery: { expected_records: 79, status: 'requires_re-extraction', source: 'https://lawlibrarysa.blogspot.com/' } };
for (const [group, paths] of Object.entries(files)) {
  const records = (await Promise.all(paths.map(async (name) => JSON.parse(await readFile(`${uploadRoot}/${name}`, 'utf8'))))).flat();
  const seenTitles = new Set(); const seenUrls = new Set(); const candidates = []; const skipped = [];
  for (const item of records) {
    const titleKey = normalizeText(item.title); const urlKey = normalizeUrl(item.link_direct || item.link_drive || item.link_telegram);
    const reasons = [];
    if (!titleKey) reasons.push('عنوان فارغ');
    if (!urlKey) reasons.push('رابط فارغ');
    if (existingTitles.has(titleKey)) reasons.push('عنوان موجود في الحالة المستعادة');
    if (urlKey && existingUrls.has(urlKey)) reasons.push('رابط موجود في الحالة المستعادة');
    if (seenTitles.has(titleKey)) reasons.push('عنوان مكرر بين الملفات');
    if (urlKey && seenUrls.has(urlKey)) reasons.push('رابط مكرر بين الملفات');
    if (reasons.length) skipped.push({ id: item.id, title: item.title, reasons });
    else { candidates.push(item); seenTitles.add(titleKey); seenUrls.add(urlKey); }
  }
  output.groups[group] = { input_files: paths, input_records: records.length, preliminary_unique_candidates: candidates.length, preliminary_skipped: skipped.length, candidates, skipped };
}
await writeFile(`${root}/lawlibrary_recovery_source_inventory.json`, `${JSON.stringify(output, null, 2)}\n`);
await writeFile(`${root}/lawlibrary_recovery_source_inventory.txt`, [
  'جرد أصول استعادة إضافات مكتبة القانون',
  `إجمالي المكنز في الحالة المستعادة: ${existing.length}`,
  '',
  ...Object.entries(output.groups).flatMap(([group, data]) => [
    `المجموعة: ${group}`,
    `- السجلات الخام: ${data.input_records}`,
    `- المرشحات الجديدة الأولية: ${data.preliminary_unique_candidates}`,
    `- المستبعد أولياً: ${data.preliminary_skipped}`,
    `- الملفات: ${data.input_files.join(' | ')}`,
    '',
  ]),
  'الاستعادة الأسبق من موقع مكتبة القانون:',
  `- سجل متوقع: ${output.initial_site_recovery.expected_records}`,
  '- الحالة: يلزم إعادة استخراج والتحقق من موقع المكتبة، ولا يعاد بناؤها بالتخمين.',
].join('\n'));
console.log(JSON.stringify({ current_total: existing.length, groups: Object.fromEntries(Object.entries(output.groups).map(([k, v]) => [k, { input: v.input_records, candidates: v.preliminary_unique_candidates, skipped: v.preliminary_skipped }])) }, null, 2));
