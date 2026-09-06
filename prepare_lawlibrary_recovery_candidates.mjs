import { readFile, writeFile } from 'node:fs/promises';

const root = process.cwd();
const uploadRoot = '/home/ubuntu/upload';
const sourceFiles = [
  ['دفعة المصادر الخمسة', 'pasted_file_Ccz0Dd_moj_official_journals_new_titles_2026-08-28.json'],
  ['دفعة المصادر الخمسة', 'pasted_file_DsF63l_lawlibrarysa_MASTER_v6_merge_ready_310.json'],
  ['دفعة المصادر الخمسة', 'pasted_file_SvnUyP_lawlibrarysa_merge_ready_140.json'],
  ['دفعة المصادر الخمسة', 'pasted_file_iRj0dd_kku_uqu_legal_new_titles_2026-08-28.json'],
  ['دفعة المصادر الخمسة', 'pasted_file_VzsweO_ksu_law_political_science_new_titles_2026-08-28.json'],
  ['جامعة الملك عبدالعزيز والقصيم', 'pasted_file_RMtfOF_kau_qassim_legal_new_titles_2026-08-28.json'],
  ['مجلة العلوم الاقتصادية والإدارية والقانونية', 'pasted_file_OsPkHo_ajsrp_saudi_legal_new_titles_24_2026-08-28.json'],
  ['جامعة المجمعة والإمام', 'pasted_file_7JojVM_majmaah_imam_legal_new_titles_2026-08-28.json'],
  ['جامعة طيبة للحقوق', 'pasted_file_0iWFJd_taibah_law_new_titles_2026-08-28.json'],
  ['أعداد مجلة جامعة طيبة للحقوق', 'pasted_file_LmV6eN_taibah_law_issues_1_2_3_8_new_titles_2026-08-28.json'],
  ['أبحاث قانونية سعودية', 'pasted_file_KlhOXH_saudi_legal_ekb_tabuk_new_titles_2026-08-28.json'],
  ['أبحاث قانونية سعودية 2024-2025', 'pasted_file_KoAqAo_ekb_saudi_legal_2024_2025_new_titles_2026-08-28.json'],
  ['أنظمة عقارية', 'pasted_file_NIf2vS_lawlibrarysa_realestate_clean_new_14_2026-08-28.json'],
];
const unwrap = (raw) => Array.isArray(raw) ? raw : raw.items;
const normalizeTitle = (value = '') => String(value)
  .normalize('NFKD')
  .replace(/[\u064B-\u065F\u0670]/g, '')
  .replace(/[أإآٱ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي')
  .replace(/[\u200e\u200f\u202a-\u202e\u2066-\u2069]/g, '')
  .toLowerCase().replace(/[^\p{L}\p{N}]/gu, '');
const normalizeUrl = (value = '') => String(value).trim().replace(/#.*$/, '').replace(/\/$/, '').toLowerCase();
const existing = unwrap(JSON.parse(await readFile(`${root}/items.json`, 'utf8')));
const existingTitles = new Set(existing.map((item) => normalizeTitle(item.title)).filter(Boolean));
const existingUrls = new Set(existing.map((item) => normalizeUrl(item.link_direct || item.link_drive || item.link_telegram)).filter(Boolean));
const seenTitles = new Set(); const seenUrls = new Set(); const candidates = []; const exclusions = [];
for (const [group, filename] of sourceFiles) {
  const entries = JSON.parse(await readFile(`${uploadRoot}/${filename}`, 'utf8'));
  for (const raw of entries) {
    const item = { ...raw, recovery_group: group, recovery_file: filename };
    const titleKey = normalizeTitle(item.title); const urlKey = normalizeUrl(item.link_direct || item.link_drive || item.link_telegram); const reasons = [];
    if (!titleKey) reasons.push('عنوان فارغ');
    if (!urlKey) reasons.push('رابط فارغ');
    if (titleKey && existingTitles.has(titleKey)) reasons.push('عنوان موجود في الحالة المستعادة');
    if (urlKey && existingUrls.has(urlKey)) reasons.push('رابط موجود في الحالة المستعادة');
    if (titleKey && seenTitles.has(titleKey)) reasons.push('عنوان مكرر ضمن ملفات الاستعادة');
    if (urlKey && seenUrls.has(urlKey)) reasons.push('رابط مكرر ضمن ملفات الاستعادة');
    if (reasons.length) exclusions.push({ id: item.id, title: item.title, link_direct: item.link_direct, recovery_group: group, recovery_file: filename, reasons });
    else { candidates.push(item); seenTitles.add(titleKey); seenUrls.add(urlKey); }
  }
}
const byGroup = Object.fromEntries(sourceFiles.map(([group]) => [group, { raw: 0, candidates: 0, exclusions: 0 }]));
for (const [group] of sourceFiles) byGroup[group].raw += 1;
for (const item of candidates) byGroup[item.recovery_group].candidates += 1;
for (const item of exclusions) byGroup[item.recovery_group].exclusions += 1;
const byOriginSource = Object.fromEntries([...candidates.reduce((map, item) => map.set(item.source || item.publisher || 'غير محدد', (map.get(item.source || item.publisher || 'غير محدد') || 0) + 1), new Map()).entries()].sort((a,b) => b[1] - a[1]));
const report = { generated_at: new Date().toISOString(), current_total: existing.length, input_file_count: sourceFiles.length, raw_input_count: candidates.length + exclusions.length, candidate_count: candidates.length, exclusion_count: exclusions.length, by_group: byGroup, by_origin_source: byOriginSource, candidates, exclusions };
await writeFile(`${root}/lawlibrary_recovery_candidates.json`, `${JSON.stringify(report, null, 2)}\n`);
await writeFile(`${root}/lawlibrary_recovery_candidates.txt`, [
  'قائمة استعادة مكتبة القانون بعد تصحيح التطبيع العربي',
  `إجمالي المكنز في الحالة المستعادة: ${existing.length}`,
  `إجمالي السجلات المقروءة: ${report.raw_input_count}`,
  `مرشحات جديدة قبل اختبار الفتح العام: ${report.candidate_count}`,
  `مستبعدات بسبب تكرار أو نقص بيانات: ${report.exclusion_count}`,
  '',
  'التوزيع بحسب المجموعة:',
  ...Object.entries(byGroup).map(([group, counts]) => `- ${group}: خام ${counts.raw} | مرشح ${counts.candidates} | مستبعد ${counts.exclusions}`),
  '',
  'التوزيع بحسب المصدر الأصلي للمرشحات:',
  ...Object.entries(byOriginSource).map(([source, count]) => `- ${source}: ${count}`),
].join('\n'));
console.log(JSON.stringify({ current_total: existing.length, raw_input_count: report.raw_input_count, candidate_count: report.candidate_count, exclusion_count: report.exclusion_count, by_group: byGroup }, null, 2));
