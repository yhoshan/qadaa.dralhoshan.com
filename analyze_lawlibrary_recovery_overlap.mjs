import { readFile, writeFile } from 'node:fs/promises';

const root = process.cwd();
const uploadRoot = '/home/ubuntu/upload';
const sourceFiles = [
  'pasted_file_Ccz0Dd_moj_official_journals_new_titles_2026-08-28.json',
  'pasted_file_DsF63l_lawlibrarysa_MASTER_v6_merge_ready_310.json',
  'pasted_file_SvnUyP_lawlibrarysa_merge_ready_140.json',
  'pasted_file_iRj0dd_kku_uqu_legal_new_titles_2026-08-28.json',
  'pasted_file_VzsweO_ksu_law_political_science_new_titles_2026-08-28.json',
  'pasted_file_RMtfOF_kau_qassim_legal_new_titles_2026-08-28.json',
  'pasted_file_OsPkHo_ajsrp_saudi_legal_new_titles_24_2026-08-28.json',
  'pasted_file_7JojVM_majmaah_imam_legal_new_titles_2026-08-28.json',
];
const unwrap = (raw) => Array.isArray(raw) ? raw : raw.items;
const normalize = (value = '') => String(value).toLowerCase().normalize('NFKD').replace(/[\u064B-\u065F\u0670]/g, '').replace(/[أإآ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي').replace(/[\s\W_]+/g, '');
const items = unwrap(JSON.parse(await readFile(`${root}/items.json`, 'utf8')));
const index = new Map();
for (const item of items) { const key = normalize(item.title); if (!index.has(key)) index.set(key, []); index.get(key).push({ id: item.id, title: item.title, source: item.source, link_direct: item.link_direct }); }
const sourceCounts = new Map(); const mismatches = []; const blankTitles = []; let rawTotal = 0; let titleMatches = 0;
for (const filename of sourceFiles) {
  const entries = JSON.parse(await readFile(`${uploadRoot}/${filename}`, 'utf8')); rawTotal += entries.length;
  for (const input of entries) {
    const titleKey = normalize(input.title);
    if (!titleKey) { blankTitles.push({ file: filename, input_id: input.id, title: input.title || '' }); continue; }
    const matches = index.get(titleKey) || [];
    if (!matches.length) { mismatches.push({ file: filename, input_id: input.id, title: input.title, input_url: input.link_direct }); continue; }
    titleMatches += 1;
    const firstMatch = matches[0];
    sourceCounts.set(firstMatch.source || 'غير محدد', (sourceCounts.get(firstMatch.source || 'غير محدد') || 0) + 1);
  }
}
const result = { generated_at: new Date().toISOString(), raw_total: rawTotal, title_matches: titleMatches, title_unmatched: mismatches.length, blank_input_titles: blankTitles.length, matching_existing_sources: Object.fromEntries([...sourceCounts.entries()].sort((a,b) => b[1] - a[1])), unmatched_examples: mismatches.slice(0, 40) };
await writeFile(`${root}/lawlibrary_recovery_overlap_analysis.json`, `${JSON.stringify(result, null, 2)}\n`);
await writeFile(`${root}/lawlibrary_recovery_overlap_analysis.txt`, [
  'تحليل تداخل ملفات استعادة مكتبة القانون مع الحالة المستعادة',
  `إجمالي الصفوف الخام: ${rawTotal}`,
  `صفوف تطابق عنواناً قائماً: ${titleMatches}`,
  `صفوف بلا تطابق عنواني: ${mismatches.length}`,
  `صفوف بعناوين فارغة: ${blankTitles.length}`,
  '',
  'مصادر السجلات المطابقة في الحالة الحالية:',
  ...[...sourceCounts.entries()].sort((a,b) => b[1] - a[1]).map(([source, count]) => `- ${source}: ${count}`),
  '',
  'أمثلة من الصفوف غير المطابقة:',
  ...(mismatches.length ? mismatches.slice(0, 40).map((row) => `- ${row.file} | ${row.input_id} | ${row.title}`) : ['- لا يوجد.']),
].join('\n'));
console.log(JSON.stringify({ raw_total: rawTotal, title_matches: titleMatches, title_unmatched: mismatches.length, blank_input_titles: blankTitles.length, matching_existing_sources: result.matching_existing_sources }, null, 2));
